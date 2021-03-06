/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This software may be used and distributed according to the terms of the
 * GNU General Public License version 2.
 */

#pragma once

#include "folly/portability/Windows.h"

#include <ProjectedFSLib.h>
#include "eden/fs/utils/PathFuncs.h"
#include "eden/fs/win/mount/FsChannel.h"
#include "eden/fs/win/utils/Guid.h"

namespace facebook {
namespace eden {
class EdenMount;
class EdenDispatcher;

class PrjfsChannel : public FsChannel {
 public:
  PrjfsChannel(const PrjfsChannel&) = delete;
  PrjfsChannel& operator=(const PrjfsChannel&) = delete;

  explicit PrjfsChannel() = delete;

  PrjfsChannel(EdenMount* mount);
  ~PrjfsChannel();
  void
  start(bool readOnly, EdenDispatcher* dispatcher, bool useNegativePathCaching);
  void stop();

  folly::SemiFuture<FsChannel::StopData> getStopFuture() override;

  /**
   * Remove files from the Projected FS cache. removeCachedFile() doesn't care
   * about the file state and will remove file in any state.
   */
  void removeCachedFile(RelativePathPiece path) override;

  void addDirectoryPlaceholder(RelativePathPiece path) override;

  void flushNegativePathCache() override;

 private:
  //
  // Channel to talk to projectedFS.
  //
  PRJ_NAMESPACE_VIRTUALIZATION_CONTEXT mountChannel_{nullptr};

  const AbsolutePath& mountPath_;
  Guid mountId_;
  bool isRunning_{false};
  bool useNegativePathCaching_{true};
  folly::Promise<FsChannel::StopData> stopPromise_;
};

} // namespace eden
} // namespace facebook
