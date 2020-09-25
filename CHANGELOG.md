# Change log of [ansible-backuppc-server](https://github.com/UdelaRInterior/ansible-backuppc) role

## [3.1.0](https://github.com/UdelaRInterior/ansible-backuppc/releases/tag/3.1.0), by @ulvida
- Default values and Access Control

## [3.0.1](https://github.com/UdelaRInterior/ansible-backuppc/releases/tag/3.0.1), by @ulvida
- Template error for string in BackupFilesOnly
- Update README and comments

## [3.0.0](https://github.com/UdelaRInterior/ansible-backuppc/releases/tag/3.0.0), by @ulvida

- refactor of all variables under `backuppc_srv_*` namespace.
- start managing RsyncShareName for backup files selection, 
- Full management of BackupFilesOnly and BackupFilesExclude
- added a lot of BackupPC parameters as variables in the role
- management of BackupPC users email, including configuration in /etc/aliases

## [2.0.0](https://github.com/UdelaRInterior/ansible-backuppc/releases/tag/2.0.0), by @ulvida

Last version used before restarting versionning.

Separation of backuppc client and server role, [backuppc_client](https://github.com/UdelaRInterior/ansible-backuppc-client/) role was already refactored after thir version of server role, but remained compatible with it.


## [1.0.2](https://github.com/UdelaRInterior/ansible-backuppc/releases/tag/1.0.2), by @HanXHX

- Fix: re-setup when any package installed

## [1.0.1](https://github.com/UdelaRInterior/ansible-backuppc/releases/tag/1.0.1), by @HanXHX

- Force install libfile-rsyncp-perl


## [1.0](https://github.com/UdelaRInterior/ansible-backuppc/releases/tag/1.0), by @HanXHX

- Display backuppc ssh pub key

