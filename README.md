# Mirror

A script to create and update mirrors of RPM repositories using `reposync`.

Runs on

* RHEL 8 (and compatible)
* RHEL 9 (and compatible)


## Installation

Clone this repo:

```bash
cd /opt
git clone --recurse-submodules https://github.com/Linuxfabrik/mirror.git
```

Create your configuration. The default path is `/etc/mirror.yml`. Have a look at the `example.yml` file and the synopsis below.

Install `yum-utils` and `createrepo`.

Use a web server that points to the directory named `base_path` in the configuration file.

If using systemd, set up the timer and service to update your mirror at regular intervals:

```bash
useradd --system --home-dir /opt/mirror --shell /bin/false mirror

cd /opt/mirror
cp -v systemd/mirror-update.service /etc/systemd/system/mirror-update.service
cp -v systemd/mirror-update.timer /etc/systemd/system/mirror-update.timer

# adjust the OnCalendar option
$EDITOR /etc/systemd/system/mirror-update.timer

systemctl daemon-reload
systemctl enable --now mirror-update.timer

# allow the mirror user to run dnf via sudo
cp -v mirror.sudoers /etc/sudoers.d/mirror

# make sure the base path exists and can be access both by the webserver user and the mirror user
webserver_user=apache
base_path='/var/www/html/github-repos'

mkdir -p "$base_path"

setfacl --recursive --modify user:$webserver_user:rwx "$base_path"
setfacl --recursive --modify user:$webserver_user:rwx "$base_path"

setfacl --recursive --modify group:$webserver_user:rx "$base_path"
setfacl --recursive --modify group:$webserver_user:rx "$base_path"

setfacl --recursive --modify user:mirror:rwx "$base_path"
setfacl --recursive --modify user:mirror:rwx --default "$base_path"
```


## How to Provide a RPM-based Repository on your Mirror Server

If you want to provide an RPM-based repository, it must be present in `/etc/yum.repos.d`. However, it does not need to be enabled, so we generally recommend disabling it (to prevent the mirror server itself from accidentally using it).

Best practice: Create a repo file named `/etc/yum.repos.d/mirror-<OS>-<Package>-<Version>.repo`. Use the same scheme for the repo filename and the repoid. Make sure you have `enabled=0` set so that the mirror itself is not using the repo.

Example: `/etc/yum.repos.d/mirror-rhel8-mariadb-10.6.repo`

```ini
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
base_path: '/var/www/html/mirror'
reposync_repos:
  - repoid: 'mirror-rhel8-mariadb-10.6'
    relative_target_path: 'MariaDB/mariadb-10.6/yum/rhel/8/x86_64'
```

Determine whether or not it is necessary to run `createrepo`. If the mirrored repo is not identical to the upstream repo (e.g. due to `includepkgs` or `excludepkgs` directives), you need to run `createrepo`. If this is not the case, you should avoid running it, as it will destroy RHEL's module information.

Now run the commands manually for the first time to accept the GPG keys. For example:

```bash
BASE_PATH='/var/www/html/mirror'
REPOID='mirror-rhel8-mariadb-10.6'
RELATIVE_TARGET_PATH='MariaDB/mariadb-10.6/yum/rhel/8/x86_64'
sudo -u mirror reposync --repoid="$REPOID" --download-path="$BASE_PATH/$RELATIVE_TARGET_PATH" --norepopath --downloadcomps --download-metadata

# createrepo "$BASE_PATH/$RELATIVE_TARGET_PATH"

chown -R apache:apache $BASE_PATH
restorecon -Fvr $BASE_PATH
```

## Synopsis - The Configuration File

`base_path`: Mandatory, string. Directory under which all the repos will be placed. This directory has to exist already and should be served by a webserver.

`reposync_repos`: Optional, list. List of repositories to mirror using `reposync`.<br>Subkeys:

* `repoid`: Mandatory, string. Repo-ID. Can be found using `dnf repolist`.
* `relative_target_path`: Mandatory, string. Target path where the repo should be placed, relative to `base_path`.
* `createrepo`: Optional, boolean. If `createrepo` should be ran on the repo after mirroring or not. Only use this if the mirrored repo is not idential to the upstream repo (for example due to `includepkgs` or `excludepkgs` directives). Else, you should avoid running it, since it destroys RHEL's module information. Defaults to `false`.


## Exit Codes

* 0: success / config valid
* 1: failed to read config / config invalid
