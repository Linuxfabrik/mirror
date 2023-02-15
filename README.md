# Mirror

A script to create and update mirrors of RPM repositories. Currently it supports:

* mirroring RPM-based repositories using `reposync`
* downloading RPM release assets from GitHub and creating a RPM repository using `createrepo`

Runs on

* RHEL 8 (and compatible)


## Installation

Clone this repo:

```bash
cd /opt
git clone --recurse-submodules https://github.com/Linuxfabrik/mirror.git
```

Create your configuration. The default path is `/etc/mirror.yml`. Have a look at the `/opt/mirror/example.yml` file and the Synopsis below.

Install `yum-utils` and `createrepo`.

Use a web server that points to the directory named `base_path` in the configuration file.

If using systemd, set up the timer and service to update your mirror at regular intervals:

```bash
cd /opt/mirror
cp -v systemd/mirror-update.service /etc/systemd/system/mirror-update.service
cp -v systemd/mirror-update.timer /etc/systemd/system/mirror-update.timer

# adjust the OnCalendar option
$EDITOR /etc/systemd/system/mirror-update.timer

systemctl daemon-reload
systemctl enable --now mirror-update.timer
```


## How to Provide a Repository on your Mirror Server

### RPM-based repository

If you want to provide an RPM-based repository, it must be present in `/etc/yum.repos.d`. However, it does not need to be enabled, so we generally recommend disabling it (to prevent the mirror server itself from accidentally using it).

Best practice: Create a repo file named `/etc/yum.repos.d/mirror-<OS>-<Package>-<Version>`. Use the same scheme for the repo filename and the repoid. Make sure you have `enabled=0` set so that the mirror itself is not using the repo.

Example: `/etc/yum.repos.d/mirror-rhel8-mariadb-10.6.repo`

```
[mirror-rhel8-mariadb-10.6]
name = MariaDB Server
baseurl = https://downloads.mariadb.com/MariaDB/mariadb-10.6/yum/rhel/8/$basearch
gpgkey = file:///etc/pki/rpm-gpg/MariaDB-Server-GPG-KEY
gpgcheck = 1
enabled=0
module_hotfixes = 1
```

In `/etc/mirror.yml`, set the location for the repo to be mirrored. This path should be unique to prevent multiple repos from overwriting each other. The path will then be created by the script.

```yaml
reposync_repos:
  - repoid: 'mirror-rhel8-mariadb-10.6'
    relative_target_path: 'MariaDB/mariadb-10.6/yum/rhel/8/x86_64'
```

Determine whether or not it is necessary to run `createrepo`. If the mirrored repo is not identical to the upstream repo (e.g. due to `includepkgs` or `excludepkgs` directives), you need to run `createrepo`. If this is not the case, you should avoid running it, as it will destroy RHEL's module information.

Now run the commands manually for the first time to accept the GPG keys. For example:

```bash
BASE_PATH='/var/www/html/mirror'
REPOID='mirror-rhel8-mariadb-10.6'
DOWNLOAD_PATH='MariaDB/mariadb-10.6/yum/rhel/8/x86_64'
reposync --repoid="$REPOID" --download-path="$BASE_PATH/$DOWNLOAD_PATH" --norepopath --downloadcomps --download-metadata

# createrepo "$BASE_PATH/$DOWNLOAD_PATH'

chown -R apache:apache $BASE_PATH
restorecon -Fvr $BASE_PATH
```


### Repo from GitHub release assets

This method allows you to create an RPM repository using RPM from the latest GitHub release of a project. For example, to create a repository for [mydumper](https://github.com/mydumper/mydumper), use the following config:

```yaml
github_repos:
  - github_user: 'mydumper'
    github_repo: 'mydumper'
    relative_target_path: 'mydumper/el/8'
    rpm_regex: 'mydumper-{latest_version}-\d\+.el8.x86_64.rpm'
```


## Synopsis - The Configuration File

`base_path`: Mandatory, string. Directory under which all the repos will be placed. This directory should be served by a webserver.

`reposync_repos`: List, optional. List of repositories to mirror using `reposync`.<br>Subkeys:

* `repoid`: Mandatory, string. Repo-ID. Can be found using `dnf repolist`.
* `relative_target_path`: Mandatory, string. Target path where the repo should be placed, relative to `base_path`.
* `createrepo`: Optional, boolean. If `createrepo` should be ran on the repo after mirroring or not. Only use this if the mirrored repo is not idential to the upstream repo (for example due to `includepkgs` or `excludepkgs` directives). Else, you should avoid running it, since it destroys RHEL 8 module information. Defaults to `false`.

`github_repos`: List, optional. List of repositories to create from GitHub the latest release assets.<br>Subkeys:

* `github_user`: Mandatory, string. The username of the GitHub repo path. For example, `'Linuxfabrik'`.
* `github_repo`: Mandatory, string. The repo name. For example, `'mirror'`.
* `relative_target_path`: Mandatory, string. Target path where the repo should be placed, relative to `base_path`.
* `rpm_regex`: Optional, string. A [Python Regular Expression](https://docs.python.org/3/howto/regex.html) which will be matched against the names of the release assets to select the correct RPM file. You can use `{latest_version}` as a placeholder, which will be replaced by the latest version (retrieved via the GitHub API) before matching. Note that the regex should only match one file, as the first matching file will be downloaded. Defaults to `'.*{latest_version}.*\.rpm'`.
* `number_of_rpms_to_keep`: Optional, int. Number of older RPM files to keep. Note that this simply deletes all older files matching `*.rpm` in the target path directory. Defaults to `3`.


# Exit Codes

* 0: success / config valid
* 1: failed to read config / config invalid
