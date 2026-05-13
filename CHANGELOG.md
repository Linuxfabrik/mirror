# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Breaking Changes

* moved functionality to create RPM repositories from GitHub releases to its own script: [github-project-createrepo](https://github.com/Linuxfabrik/github-project-createrepo)
* the built-in special case that synced all versions for any repository whose ID contained `icinga` has been removed. Such repositories now follow the global default (`--newest-only`) unless `newest_only: false` is set explicitly per repository in `/etc/mirror.yml`. Admins who relied on the previous implicit behavior must add `newest_only: false` to those entries, otherwise older package versions will be deleted on the next mirror run.

### Added

* per-repository `newest_only` option in `/etc/mirror.yml` (boolean, default `true`) to control whether `reposync` mirrors only the newest version of each package or all versions; set to `false` for repositories like Icinga that need to keep older versions

### Fixed

* mirror failing to update due wrong sudoers entry