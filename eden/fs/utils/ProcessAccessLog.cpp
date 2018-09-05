/*
 *  Copyright (c) 2018-present, Facebook, Inc.
 *  All rights reserved.
 *
 *  This source code is licensed under the BSD-style license found in the
 *  LICENSE file in the root directory of this source tree. An additional grant
 *  of patent rights can be found in the PATENTS file in the same directory.
 *
 */
#include "ProcessAccessLog.h"

#include <folly/Exception.h>
#include <folly/MapUtil.h>
#include <folly/MicroLock.h>
#include <folly/ThreadLocal.h>
#include "eden/fs/utils/ProcessNameCache.h"

namespace facebook {
namespace eden {

struct ThreadLocalBucket {
  explicit ThreadLocalBucket(ProcessAccessLog* processAccessLog)
      : state_{folly::in_place, processAccessLog} {}

  ~ThreadLocalBucket() {
    // This thread is going away, so merge our data into the parent.
    mergeUpstream();
  }

  /**
   * Returns whether the pid was newly-recorded in this thread-second or not.
   */
  bool add(uint64_t secondsSinceStart, pid_t pid) {
    auto state = state_.lock();

    // isNewPid must be initialized because BucketedLog::add will not call
    // Bucket::add if secondsSinceStart is too old and the sample is dropped.
    // (In that case, it's unnecessary to record the process name.)
    bool isNewPid = false;
    state->buckets.add(secondsSinceStart, pid, isNewPid);
    return isNewPid;
  }

  void mergeUpstream() {
    auto state = state_.lock();
    if (!state->owner) {
      return;
    }
    state->owner->state_.withWLock(
        [&](auto& ownerState) { ownerState.buckets.merge(state->buckets); });
    state->buckets.clear();
  }

  void clearOwnerIfMe(ProcessAccessLog* owner) {
    auto state = state_.lock();
    if (state->owner == owner) {
      state->owner = nullptr;
    }
  }

 private:
  /**
   * Sadly, because getAllAccesses needs to access all of the buckets, it
   * needs a mechanism to stop writers for the duration of the read.
   *
   * Reading the data (merging up-stream from all of the threads) is
   * exceptionally rare, so this lock should largely stay uncontended. I
   * considered using folly::SpinLock, but the documentation strongly suggests
   * not. I am hoping that acquiring an uncontended MicroLock
   * boils down to a single CAS, even though lock xchg can be painful by itself.
   *
   * This lock must always be acquired before the owner's buckets lock.
   */
  struct State {
    explicit State(ProcessAccessLog* pal) : owner{pal} {}
    ProcessAccessLog::Buckets buckets;
    ProcessAccessLog* owner;
  };

  struct InitedMicroLock : folly::MicroLock {
    InitedMicroLock() {
      init();
    }
  };
  folly::Synchronized<State, InitedMicroLock> state_;
};

namespace {
struct BucketTag;
folly::ThreadLocalPtr<ThreadLocalBucket, BucketTag> threadLocalBucketPtr;
} // namespace

void ProcessAccessLog::Bucket::clear() {
  accessCounts.clear();
}

void ProcessAccessLog::Bucket::add(pid_t pid, bool& isNew) {
  auto [iter, inserted] = accessCounts.emplace(pid, 1);
  if (!inserted) {
    ++iter->second;
  }
  isNew = inserted;
}

void ProcessAccessLog::Bucket::merge(const Bucket& other) {
  for (auto& [pid, otherCount] : other.accessCounts) {
    accessCounts[pid] += otherCount;
  }
}

ProcessAccessLog::ProcessAccessLog(
    std::shared_ptr<ProcessNameCache> processNameCache)
    : processNameCache_{std::move(processNameCache)} {}

ProcessAccessLog::~ProcessAccessLog() {
  for (auto& tlb : threadLocalBucketPtr.accessAllThreads()) {
    tlb.clearOwnerIfMe(this);
  }
}

void ProcessAccessLog::recordAccess(pid_t pid) {
  // This function is called very frequently from different threads. It's a
  // write-often, read-rarely use case, so, to avoid synchronization overhead,
  // record to thread-local storage and only merge into the access log when the
  // calling thread dies or when the data must be read.

  auto tlb = threadLocalBucketPtr.get();
  if (!tlb) {
    threadLocalBucketPtr.reset(std::make_unique<ThreadLocalBucket>(this));
    tlb = threadLocalBucketPtr.get();
  }

  uint64_t secondsSinceEpoch =
      std::chrono::duration_cast<std::chrono::seconds>(
          std::chrono::steady_clock::now().time_since_epoch())
          .count();

  bool isNewPid = tlb->add(secondsSinceEpoch, pid);

  // Many processes are short-lived, so grab the executable name during the
  // access. We could potentially get away with grabbing executable names a bit
  // later on another thread, but we'll only readlink() once per pid.

  // Sometimes we receive requests from pid 0. Record the access,
  // but don't try to look up a name.
  if (pid) {
    // Since recordAccess is called a lot by latency- and throughput-sensitive
    // code, only try to lookup and cache the process name if we haven't seen it
    // this thread-second.
    if (isNewPid) {
      // It's a bit unfortunate that ProcessNameCache maintains its own
      // SharedMutex, but it will be shared with thrift counters.
      processNameCache_->add(pid);
    }
  }
}

std::unordered_map<pid_t, size_t> ProcessAccessLog::getAllAccesses(
    std::chrono::seconds lastNSeconds) {
  auto secondCount = lastNSeconds.count();
  // First, merge all the thread-local buckets into their owners, including us.
  for (auto& tlb : threadLocalBucketPtr.accessAllThreads()) {
    // This must be done outside of acquiring our own state_ lock.
    tlb.mergeUpstream();
  }

  uint64_t secondsSinceEpoch =
      std::chrono::duration_cast<std::chrono::seconds>(
          std::chrono::steady_clock::now().time_since_epoch())
          .count();

  auto state = state_.wlock();
  auto allBuckets = state->buckets.getAll(secondsSinceEpoch);

  if (secondCount < 0) {
    return {};
  }

  Bucket bucket;
  uint64_t count =
      std::min(allBuckets.size(), static_cast<uint64_t>(secondCount));
  for (auto iter = allBuckets.end() - count; iter != allBuckets.end(); ++iter) {
    bucket.merge(*iter);
  }
  return bucket.accessCounts;
}

} // namespace eden
} // namespace facebook
