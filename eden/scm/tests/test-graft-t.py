# coding=utf-8

# coding=utf-8

    ├─╮
    │ o  test@5.draft: 5
    │ │
    o │  test@4.draft: 4
    ├─╯
    │
    │
    │
    │
    │
    │
    │
    │
    │ o    test@6.draft: 6
    │ ├─╮
    │ │ o  test@5.draft: 5
    │ │ │
    │ o │  test@4.draft: 4
    │ ├─╯
    │ o  baz@3.public: 3
    │ │
    │ o  test@2.public: 2
    │ │
    │ o  bar@1.public: 1
    ├─╯
    │
    │
    │ o  1
    ├─╯
    │
    │ o  2
    ├─╯
    │ o  1
    ├─╯
    │  user:        test
    │  date:        Thu Jan 01 00:00:00 1970 +0000
    │  summary:     D0
    │
    │  user:        test
    │  date:        Thu Jan 01 00:00:00 1970 +0000
    │  summary:     C0
    │
    │  user:        test
    │  date:        Thu Jan 01 00:00:00 1970 +0000
    │  summary:     B0
    │
    │  user:        test
    │  date:        Thu Jan 01 00:00:00 1970 +0000
    │  summary:     E0
    │
    │ o  commit:      560daee679da
    │ │  user:        test
    │ │  date:        Thu Jan 01 00:00:00 1970 +0000
    │ │  summary:     D1
    │ │
    │ o  commit:      c9763722f9bd
    ├─╯  user:        test
    │    date:        Thu Jan 01 00:00:00 1970 +0000
    │    summary:     C1
    │
    │ o  commit:      b69f5839d2d9
    │ │  user:        test
    │ │  date:        Thu Jan 01 00:00:00 1970 +0000
    │ │  summary:     D0
    │ │
    │ o  commit:      f58c7e2b28fa
    │ │  user:        test
    │ │  date:        Thu Jan 01 00:00:00 1970 +0000
    │ │  summary:     C0
    │ │
    │ o  commit:      3d7bba921b5d
    ├─╯  user:        test
    │    date:        Thu Jan 01 00:00:00 1970 +0000
    │    summary:     B0
    │
    │  user:        test
    │  date:        Thu Jan 01 00:00:00 1970 +0000
    │  files:       f3d f4e
    │  description:
    │  D2
    │
    │
    │  diff --git a/f3d b/f3d
    │  new file mode 100644
    │  --- /dev/null
    │  +++ b/f3d
    │  @@ -0,0 +1,1 @@
    │  +c3a
    │  diff --git a/f4e b/f4e
    │  --- a/f4e
    │  +++ b/f4e
    │  @@ -1,1 +1,1 @@
    │  -c4a
    │  +c4d
    │
    │  user:        test
    │  date:        Thu Jan 01 00:00:00 1970 +0000
    │  files:       f1e f2a f2c f5a f5b
    │  copies:      f2c (f2a) f5a (f5b)
    │  description:
    │  C2
    │
    │
    │  diff --git a/f1e b/f1e
    │  --- a/f1e
    │  +++ b/f1e
    │  @@ -1,1 +1,1 @@
    │  -c1a
    │  +c1c
    │  diff --git a/f2a b/f2c
    │  rename from f2a
    │  rename to f2c
    │  diff --git a/f5b b/f5a
    │  rename from f5b
    │  rename to f5a
    │  --- a/f5b
    │  +++ b/f5a
    │  @@ -1,1 +1,1 @@
    │  -c5a
    │  +c5c
    │
    │  user:        test
    │  date:        Thu Jan 01 00:00:00 1970 +0000
    │  files:       f1a f1e f2a f3a f3e f4a f4e f5a f5b
    │  copies:      f1e (f1a) f3e (f3a) f4e (f4a) f5b (f5a)
    │  description:
    │  E0
    │
    │
    │  diff --git a/f1a b/f1e
    │  rename from f1a
    │  rename to f1e
    │  diff --git a/f2a b/f2a
    │  --- a/f2a
    │  +++ b/f2a
    │  @@ -1,1 +1,1 @@
    │  -c2a
    │  +c2e
    │  diff --git a/f3a b/f3e
    │  rename from f3a
    │  rename to f3e
    │  diff --git a/f4a b/f4e
    │  rename from f4a
    │  rename to f4e
    │  diff --git a/f5a b/f5b
    │  rename from f5a
    │  rename to f5b
    │
    │ o  commit:      560daee679da
    │ │  user:        test
    │ │  date:        Thu Jan 01 00:00:00 1970 +0000
    │ │  files:       f3d f4a
    │ │  description:
    │ │  D1
    │ │
    │ │
    │ │  diff --git a/f3d b/f3d
    │ │  new file mode 100644
    │ │  --- /dev/null
    │ │  +++ b/f3d
    │ │  @@ -0,0 +1,1 @@
    │ │  +c3a
    │ │  diff --git a/f4a b/f4a
    │ │  --- a/f4a
    │ │  +++ b/f4a
    │ │  @@ -1,1 +1,1 @@
    │ │  -c4a
    │ │  +c4d
    │ │
    │ o  commit:      c9763722f9bd
    ├─╯  user:        test
    │    date:        Thu Jan 01 00:00:00 1970 +0000
    │    files:       f1a f2a f2c f5a
    │    copies:      f2c (f2a)
    │    description:
    │    C1
    │
    │
    │    diff --git a/f1a b/f1a
    │    --- a/f1a
    │    +++ b/f1a
    │    @@ -1,1 +1,1 @@
    │    -c1a
    │    +c1c
    │    diff --git a/f2a b/f2c
    │    rename from f2a
    │    rename to f2c
    │    diff --git a/f5a b/f5a
    │    --- a/f5a
    │    +++ b/f5a
    │    @@ -1,1 +1,1 @@
    │    -c5a
    │    +c5c
    │
    │ o  commit:      b69f5839d2d9
    │ │  user:        test
    │ │  date:        Thu Jan 01 00:00:00 1970 +0000
    │ │  files:       f3b f3d f4a
    │ │  copies:      f3d (f3b)
    │ │  description:
    │ │  D0
    │ │
    │ │
    │ │  diff --git a/f3b b/f3d
    │ │  rename from f3b
    │ │  rename to f3d
    │ │  diff --git a/f4a b/f4a
    │ │  --- a/f4a
    │ │  +++ b/f4a
    │ │  @@ -1,1 +1,1 @@
    │ │  -c4a
    │ │  +c4d
    │ │
    │ o  commit:      f58c7e2b28fa
    │ │  user:        test
    │ │  date:        Thu Jan 01 00:00:00 1970 +0000
    │ │  files:       f1b f2a f2c f5a f5b
    │ │  copies:      f2c (f2a) f5a (f5b)
    │ │  description:
    │ │  C0
    │ │
    │ │
    │ │  diff --git a/f1b b/f1b
    │ │  --- a/f1b
    │ │  +++ b/f1b
    │ │  @@ -1,1 +1,1 @@
    │ │  -c1a
    │ │  +c1c
    │ │  diff --git a/f2a b/f2c
    │ │  rename from f2a
    │ │  rename to f2c
    │ │  diff --git a/f5b b/f5a
    │ │  rename from f5b
    │ │  rename to f5a
    │ │  --- a/f5b
    │ │  +++ b/f5a
    │ │  @@ -1,1 +1,1 @@
    │ │  -c5a
    │ │  +c5c
    │ │
    │ o  commit:      3d7bba921b5d
    ├─╯  user:        test
    │    date:        Thu Jan 01 00:00:00 1970 +0000
    │    files:       f1a f1b f3a f3b f5a f5b
    │    copies:      f1b (f1a) f3b (f3a) f5b (f5a)
    │    description:
    │    B0
    │
    │
    │    diff --git a/f1a b/f1b
    │    rename from f1a
    │    rename to f1b
    │    diff --git a/f3a b/f3b
    │    rename from f3a
    │    rename to f3b
    │    diff --git a/f5a b/f5b
    │    rename from f5a
    │    rename to f5b
    │