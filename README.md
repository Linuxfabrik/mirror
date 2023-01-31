# Mirror

A script to create and update mirrors of RPM repositories. Currently it supports:

* mirroring RPM-based repositories using `reposync`
* downloading RPM release assets from GitHub and creating a RPM repository using `createrepo`

Runs on

* RHEL 8 (and compatible)


## Mandatory Requirements

* Clone this repo:
```bash
cd /opt
git clone --recurse-submodules https://github.com/Linuxfabrik/mirror.git
```
* Create your configuration. The default path is `/etc/mirror.yml`.
* Install `yum-utils` and `createrepo`.
* Point a webserver to the directory (`base_path` in the config).


## Optional Requirements

* If using systemd, set up the timer and service:
```bash
cd /opt/mirror
cp -v systemd/mirror-update.service /etc/systemd/system/mirror-update.service
cp -v systemd/mirror-update.timer /etc/systemd/system/mirror-update.timer

# adjust the OnCalendar option
$EDITOR /etc/systemd/system/mirror-update.timer

systemctl daemon-reload
systemctl enable --now mirror-update.timer
```


## Configuration

Have a look at the `/opt/mirror/example.yml` file.

Keys:

* `base_path`: Mandatory, string. Directory under which all the repos will be placed. This directory should be served by a webserver.
* `reposync_repos`: List, optional. List of repositories to mirror using `reposync`.<br>Subkeys:
    * `repoid`: Mandatory, string. Repo-ID. Can be found using `dnf repolist`.
    * `relative_target_path`: Mandatory, string. Target path where the repo should be placed, relative to `base_path`.
    * `createrepo`: Optional, boolean. If `createrepo` should be ran on the repo after mirroring or not. Only use this if the mirrored repo is not idential to the upstream repo (for example due to `includepkgs` or `excludepkgs` directives). Else, you should avoid running it, since it destroys RHEL 8 module information. Defaults to `false`.
* `github_repos`: List, optional. List of repositories to create from GitHub the latest release assets.<br>Subkeys:
    * `github_user`: Mandatory, string. The username of the GitHub repo path. For example, `'Linuxfabrik'`.
    * `github_repo`: Mandatory, string. The repo name. For example, `'mirror'`.
    * `relative_target_path`: Mandatory, string. Target path where the repo should be placed, relative to `base_path`.
    * `rpm_regex`: Optional, string. A [Python Regular Expression](https://docs.python.org/3/howto/regex.html) which will be matched against the names of the release assets to select the correct RPM file. You can use `{latest_version}` as a placeholder, which will be replaced by the latest version (retrieved via the GitHub API) before matching. Note that the regex should only match one file, as the first matching file will be downloaded. Defaults to `'.*{latest_version}.*\.rpm'`.
    * `number_of_rpms_to_keep`: Optional, int. Number of older RPM files to keep. Note that this simply deletes all older files matching `*.rpm` in the target path directory. Defaults to `3`.


### RPM-based repositories

For this method to work, the repository needs to exist in `/etc/yum.repos.d`. However, it does not need to be enabled, therefore we generally recommend to disable them (to prevent the mirror server itself from accidentally using them).

1. Create the repo file in `/etc/yum.repos.d`.
2. Prefix the file and the repoid if the repo is for a different OS. For example, you should prefix all CentOS 7 repos using `centos7-`.
3. Edit the repo file and set `enabled=0` so that the mirror itself is not using the repo.
4. Choose a target path. This path should be unique, to prevent multiple repos from overwriting eachother. If this is the case, insert the repo name or repoid somewhere in the target path. The path is then created by the script.
5. Determine if running `createrepo` is necessary or not. If the mirrored repo is not identical to the upstream repo (for example due to `includepkgs` or `excludepkgs` directives), you need to run `createrepo`. If this is not the case, you should avoid running it, since it destroys RHEL 8 module information.
6. Run the commands manually for the first time to accept the GPG keys. For example:
```bash
reposync --repoid='rocky8-baseos' --download-path='/var/www/html/mirror/rocky/8/BaseOS/x86_64/os/' --norepopath --downloadcomps --download-metadata

# createrepo '/var/www/html/mirror/rocky/8/BaseOS/x86_64/os/' 

chown -R apache:apache /var/www/html
restorecon -Fvr /var/www/html
```
7. Add the repo to the `reposync_repos` key in your config. For example:
```yaml
base_path: '/var/www/html/mirror'
reposync_repos:
  - repoid: 'rocky8-appstream'
    relative_target_path: 'rocky/8/AppStream/x86_64/os/'
```


### Repo from GitHub release assets

This method allows creating a RPM-repository using RPM from the latest GitHub release of a project. For example, to create a repository for [mydumper](https://github.com/mydumper/mydumper), use the following config:

```yaml
base_path: '/var/www/html/mirror'
github_repos:
  - github_user: 'mydumper'
    github_repo: 'mydumper'
    relative_target_path: 'mydumper/el/8'
    rpm_regex: 'mydumper-{latest_version}-\d\+.el8.x86_64.rpm'
```


# Exit Codes

* 0: success / config valid
* 1: failed to read config / config invalid
