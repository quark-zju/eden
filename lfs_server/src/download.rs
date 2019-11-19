/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This software may be used and distributed according to the terms of the
 * GNU General Public License found in the LICENSE file in the root
 * directory of this source tree.
 */

use failure_ext::chain::ChainExt;
use futures::Stream;
use futures_ext::StreamExt;
use futures_preview::compat::Future01CompatExt;
use gotham::state::State;
use gotham_derive::{StateData, StaticResponseExtender};
use serde::Deserialize;

use filestore::{self, FetchKey};
use mononoke_types::ContentId;
use stats::{define_stats, Timeseries};

use crate::errors::ErrorKind;
use crate::http::{HttpError, StreamBody, TryIntoResponse};
use crate::lfs_server_context::RepositoryRequestContext;
use crate::middleware::LfsMethod;

define_stats! {
    prefix = "mononoke.lfs.download";
    size_bytes_sent: timeseries("size_bytes_sent"; SUM; 5, 15, 60),
}

#[derive(Deserialize, StateData, StaticResponseExtender)]
pub struct DownloadParams {
    repository: String,
    content_id: String,
}

pub async fn download(state: &mut State) -> Result<impl TryIntoResponse, HttpError> {
    let DownloadParams {
        repository,
        content_id,
    } = state.take();

    let ctx =
        RepositoryRequestContext::instantiate(state, repository.clone(), LfsMethod::Download)?;

    let content_id = ContentId::from_str(&content_id)
        .chain_err(ErrorKind::InvalidContentId)
        .map_err(HttpError::e400)?;

    // Query a stream out of the Filestore
    let fetch_stream = filestore::fetch_with_size(
        &ctx.repo.get_blobstore(),
        ctx.ctx.clone(),
        &FetchKey::Canonical(content_id),
    )
    .compat()
    .await
    .chain_err(ErrorKind::FilestoreReadFailure)
    .map_err(HttpError::e500)?;

    // Return a 404 if the stream doesn't exist.
    let (stream, size) = fetch_stream
        .ok_or_else(|| ErrorKind::ObjectDoesNotExist(content_id))
        .map_err(HttpError::e404)?;

    let stream = if ctx.config.track_bytes_sent {
        stream
            .inspect(|bytes| STATS::size_bytes_sent.add_value(bytes.len() as i64))
            .left_stream()
    } else {
        stream.right_stream()
    };

    Ok(StreamBody::new(
        stream,
        size,
        mime::APPLICATION_OCTET_STREAM,
    ))
}
