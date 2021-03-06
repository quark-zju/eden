/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This software may be used and distributed according to the terms of the
 * GNU General Public License version 2.
 */

use std::collections::HashMap;

use blobrepo::BlobRepo;
use bookmarks::{BookmarkUpdateReason, BundleReplay};
use bookmarks_types::BookmarkName;
use context::CoreContext;
use metaconfig_types::{BookmarkAttrs, InfinitepushParams, PushrebaseParams};
use mononoke_types::{BonsaiChangeset, ChangesetId};

use crate::{BookmarkKindRestrictions, BookmarkMoveAuthorization, BookmarkMovementError};

pub struct CreateBookmarkOp<'op> {
    bookmark: &'op BookmarkName,
    target: ChangesetId,
    reason: BookmarkUpdateReason,
    auth: BookmarkMoveAuthorization,
    kind_restrictions: BookmarkKindRestrictions,
    new_changesets: HashMap<ChangesetId, BonsaiChangeset>,
    bundle_replay: Option<&'op dyn BundleReplay>,
}

#[must_use = "CreateBookmarkOp must be run to have an effect"]
impl<'op> CreateBookmarkOp<'op> {
    pub fn new(
        bookmark: &'op BookmarkName,
        target: ChangesetId,
        reason: BookmarkUpdateReason,
    ) -> CreateBookmarkOp<'op> {
        CreateBookmarkOp {
            bookmark,
            target,
            reason,
            auth: BookmarkMoveAuthorization::Context,
            kind_restrictions: BookmarkKindRestrictions::AnyKind,
            new_changesets: HashMap::new(),
            bundle_replay: None,
        }
    }

    pub fn only_if_scratch(mut self) -> Self {
        self.kind_restrictions = BookmarkKindRestrictions::OnlyScratch;
        self
    }

    pub fn only_if_public(mut self) -> Self {
        self.kind_restrictions = BookmarkKindRestrictions::OnlyPublic;
        self
    }

    pub fn with_bundle_replay_data(mut self, bundle_replay: Option<&'op dyn BundleReplay>) -> Self {
        self.bundle_replay = bundle_replay;
        self
    }

    /// Include bonsai changesets for changesets that have just been added to
    /// the repository.
    pub fn with_new_changesets(
        mut self,
        changesets: HashMap<ChangesetId, BonsaiChangeset>,
    ) -> Self {
        if self.new_changesets.is_empty() {
            self.new_changesets = changesets;
        } else {
            self.new_changesets.extend(changesets.into_iter());
        }
        self
    }

    pub async fn run(
        self,
        ctx: &'op CoreContext,
        repo: &'op BlobRepo,
        infinitepush_params: &'op InfinitepushParams,
        pushrebase_params: &'op PushrebaseParams,
        bookmark_attrs: &'op BookmarkAttrs,
    ) -> Result<(), BookmarkMovementError> {
        self.auth
            .check_authorized(ctx, bookmark_attrs, self.bookmark)?;

        let is_scratch = self
            .kind_restrictions
            .check_kind(infinitepush_params, self.bookmark)?;

        let mut txn = repo.update_bookmark_transaction(ctx.clone());
        let mut txn_hook = None;

        if is_scratch {
            txn.create_scratch(self.bookmark, self.target)?;
        } else {
            crate::globalrev_mapping::require_globalrevs_disabled(pushrebase_params)?;
            txn_hook = crate::git_mapping::populate_git_mapping_txn_hook(
                ctx,
                repo,
                pushrebase_params,
                self.target,
                &self.new_changesets,
            )
            .await?;
            txn.create(self.bookmark, self.target, self.reason, self.bundle_replay)?;
        }

        let ok = match txn_hook {
            Some(txn_hook) => txn.commit_with_hook(txn_hook).await?,
            None => txn.commit().await?,
        };
        if !ok {
            return Err(BookmarkMovementError::TransactionFailed);
        }
        Ok(())
    }
}
