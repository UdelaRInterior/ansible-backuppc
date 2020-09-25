BackupPC Server Ansible role
=====================

This role, `backuppc_server` installs and configures a BackupPC server on a Debian GNU/Linux operating system. It initially worked on Debian Jessie, and is maintained up to Debian Buster. It probably can work on Ubuntu or other Debian-based systems, but it wasn't tested (PR and other contributions accepted).

It has a sister role [BackupPC client](https://github.com/UdelaRInterior/ansible-backuppc-client/) to configure client hosts that will be backed up by the BackupPC server. 

Description
------------

This role installs and configures backuppc debian package, including ther creation of an ssh key for the backuppc user, as well as passwords and e-mails for web backuppc users. Optionally, it can also (by default it does) configure Apache2 for https web access to BackupPC interface, using either a self-signed certificate, a certbot one (generated elsewhere), or your own one.     

[`backuppc_client` role](https://github.com/UdelaRInterior/ansible-backuppc-client/) configures clients' accounts in their BackupPC server, as well as server ssh access to the client, to perform backups.  But clients can also be configured manually, or by any other mean.

Notes
----

- backuppc debian package has changed its behaviour in buster, and now the web interface of BackupPC, morover its https authentication, is only available on localhost. Te role adopts this new security feature, and makes it configurable.  With default values of the role you will need to find a way to acces from the host itsef, for instance with an ssh tunnel: 
```
ssh -L 8443:localhost:443 bacuppc.domain.org
``` 
And then you access from a browser the URL https://localhost:8443/backuppc/

- The role can now handle most useful backuppc parameters but, at this time, it is designed and developed to configure backups only via rsync transfer method, with its default transport ssh ('rsync' for `XferMethod` BackupPC parameter).

 - The role handles [a bug](https://sourceforge.net/p/backuppc/mailman/message/27544764/) of BackupPC and/or its Debian packaging, that happens when IPv6 is enabled on the host where BackupPC is installed, and prevents BackupPC pinging the client, and therefore performing a backup. 

Role Variables
--------------

- `backuppc_srv_server_name`: fqdn of the host where BackupPC server is to be installed (default: `inventory_host` variable's value)

### BackupPC package

There is no reason to change the following variables, there are more to centralise values than to be modified. Note that they are note taken into account in debial packages configuration. 

- `backuppc_srv_unix_user`: BackupPC unix user in the server, from which are launched ssh backups to the client (default: `backuppc`)
- `backuppc_srv_unix_group`: BackupPC unix group in the server (default: `www-data`)
- `backuppc_srv_user_home`: Home directory of `backuppc_srv_unix_user` unix user previously defined (default: `/var/lib/backuppc`)
- `backuppc_srv_ssh_key_bits`: set length of ssh key pair (optional, default 2048)
- `backuppc_srv_config_dir`: backuppc package configuration directory (default: `/etc/backuppc`) 

### BackupPC configuration variables

These are the most important configuration variables of the role. 

See file [templates/etc/backuppc/config.pl.j2](templates/etc/backuppc/config.pl.j2) and [BackupPC documentation](https://backuppc.github.io/backuppc/BackupPC.html#Configuration-Parameters) for variables' reoles explanation and possible values. Only most significant parameters are mentionned here. 

The role's variables are named with the namespace prefix `backuppc_srv_` followed by the BackupPC `config.pl` file parameter name. Note that half of the name is in snake_case and half in CamelCase. 

#### What to backup and when to do it

The following parameters can be overwritten in a per client bases. See [`backuppc_client` role](https://github.com/UdelaRInterior/ansible-backuppc-client/blob/master/README.md)

- `backuppc_srv_RsyncShareName`: List of folders of the client to backup. An rsync will be performed by the server into the client. We advise you to always set your own value, but default value is: 
```yaml
- /etc    
- /var
- /home
- /root
```
Note: as stated above, only rsync is considered as transfer method, so we don't mention `SmbShareName`, `TarShareName`, other similar parameters, and related. 

- `backuppc_srv_BackupFilesOnly`: List of directories or files to include in backups. This can be set to a string, a list of strings, or, in the case of multiple shares, a dict of strings or lists. A dict is used to give a list of directories or files to backup for each share (the share name is the key). If a dict is used, a special key `"*"` means it applies to all shares that don't have a specific entry.

For instance, the following configuration parameters: 
```yaml
backuppc_RsyncShareName:
- /etc/gitlab
- /var/opt/gitlab

backuppc_srv_BackupFilesOnly:
  # Configuration archives fo GitLab instance:
  "/etc/gitlab":
    - /gitlab.rb
    - /gitlab-secrets.json
  # Gotlab backup file
  "/var/opt/gitlab":
    - /backups/dump_backuppc_gitlab_backup.tar
```
will perform the backup of the three needed file of a GitLab instance. (`dump_backuppc_gitlab_backup.tar` is built by a script just before the dump, see [`backuppc_client` role's documentation](https://github.com/UdelaRInterior/ansible-backuppc-client/blob/master/README.md#clients-backup-configuration-in-the-server)

- `backuppc_srv_RsyncShareName`: List of directories or files to exclude from the backup. Syntax is similar than `backuppc_srv_BackupFilesOnly`.

- `backuppc_srv_FullPeriod`: Minimum period in days between full backups (default 6.97, one week)
- `backuppc_srv_IncrPeriod`: Minimum period in days between incremental backups (default 0.97, one day)

- `backuppc_srv_FullKeepCnt`: Number of full backups to keep. A list of values, separated by commas, is admitted, in wich case it means the number of backups of periods of powers of 2: 1 week, 2 weeks, 4 weeks, etc. For insance: `4, 0, 4, 0, 0, 2` will keep 4 backups at 1 week interval, 4 backups at 16 weeks intervals (4 month) and 2 at an interval of 32 weeks (8 month, oldest backup 16 month). [templates/etc/backuppc/config.pl.j2](templates/etc/backuppc/config.pl.j2), lines 421 to 495. 

- `backuppc_srv_BackupsDisable`: Whether automatic and manual backup are disables. Default value: `0`, backups are performed regularly. Other possible values are 1: automatic backup disable, manual backup ok, 2: no backup at all.  

- `backuppc_srv_XferMethod`: What transport method to use to backup each host. Possible values are `smb`,`rsync`, `rsyncd`, `tar` and `archive` but, as stated before, the role is yet only designed for `rsync`, which obviously is the default value. 

#### Email reminders, status and messages

- `backuppc_srv_EMailFromUserName`: Name to use as the "from" name for email (Default: `backuppc_srv_unix_user` variable value),
- `backuppc_srv_EMailAdminUserName`: Destination address to an administrative user who will receive a nightly email with warnings and errors (Default: `backuppc_srv_unix_user` variable value),
- `backuppc_srv_EMailUserDestDomain`: Destination domain name for email sent to users (Default value: '', empty string)

#### CGI user interface configuration settings
Can be overridden in the per-client config.pl

- `backuppc_srv_CgiAdminUserGroup`: Linux group of admin users through the CGI (Default: `backuppc_srv_unix_user` variable value),
- `backuppc_srv_CgiAdminUsers`: List of users who are also admin users through the CGI (Default: `backuppc_srv_unix_user` variable value),
- `backuppc_srv_CgiURL`: URL of the BackupPC_Admin CGI script.  Used for email messages (Default value: `'https://{{ backuppc_srv_server_name }}/backuppc/index.cgi'`)
- `backuppc_srv_language`: Web interface's language. Default 'en', English,
- `backuppc_srv_Date_Format`: date format of the web interface. 1: US-style, 2: full format, 0. International format (role's default value) 


See also [README of backuppc-client role](https://github.com/UdelaRInterior/ansible-backuppc-client/blob/master/README.md) for detailed client variables. 

### BackuPC CGI interface / web users

`backuppc_srv_web_users`: List of web user accounts data for BackupPC (Default value is empty). It is a list of dicts, each one defing a user account with the following parameters: 
- `name`: the username of the account, to be enterd in the web interface 
- The password can be defined explicitely, or only by its hash code. For each user you should define either: 
  - `password`: the password itself, which value should be set froma vault: `'{{ vault_secret }}'`
  - `htpasswd_hash`: the hash-code of the password, generated by the user herself.  
- `mail`: (optional) the e-mail of the user, where will be sent the reports of backuppc about the managed hosts. the e-mail will be configured in the `/etc/alias` file of the host for effective mail delivery. We prefer this design than the `backuppc_srv_EMailUserDestDomain` mechanism of BackupPC, that uses a signe domain for all users. 

Usernames and their password hashcode will be configured in the `/etc/backuppc/htpasswd/` of the host. 

An htpasswd hash code for a user and a password can be obtaind running: 
```bash
htpasswd -n user 
```
htpasswd utility is installed in linux with `apache2-utils` debian package. 

In [`backuppc_client` role](https://github.com/UdelaRInterior/ansible-backuppc-client/), you will be able to configure these users in `backuppc_server_web_main_user` and `backuppc_server_web_other_users` variables. 

### Apache2 configuration

## Apache2 parameters

- `backuppc_srv_configure_apache`: Flag, whether to configure apache2 or not (Default: true),
- `backuppc_srv_disable_apache_default_site`: Flag to disable the default Apache2 VirtualHost (apache site) (Default: true),
- `backuppc_srv_apache_email`: e-mail configured in Apache2 VirtualHosts (Default value: `'webmaster@{{ ansible_fqdn }}'`

## SSL Configuration

The role can user either valide certificates generated elsewhere by Certbot, or the `ssl-certs` package's self-signed certificate.    
Configuration of SSLCertificateFile and SSLCertificateKeyFile for 

- `backuppc_srv_apache_require_ssl`: Flag to force https when accessing /backuppc CGI alias (Default: true)

- `backuppc_srv_apache_ssl_certbot`: A flag to choose the certificates to configure in Apache VHost (Default value: `false`):
  - if you use certbot to generate SSL certificates for Apache2 (eventually with an appropriate Ansible role) set this flag to true. The role will search the SSL certificate and key in tjhe folder `/etc/letsencrypt/live/{{ backuppc_srv_server_name  }}`.
  - if you want to use Apache2 with pre-generated snakeoil certificates, let it as false 

Previous flag defines the variables `backuppc_srv_apache_ssl_cert_file` and `backuppc_srv_apache_ssl_cert_key_file` used for Apache configuration of ssl certificates. You can overwrithe these variables with custom values, in which case porevious flag will be unuseful.

## Access control

- `backuppc_srv_apache_access_control`: a flag to configure Require directives hereafter (default: `true`)
- `backuppc_srv_apache_Require`: the value of [Apache Require directive](https://httpd.apache.org/docs/2.4/mod/mod_authz_host.html#requiredirectives) to restrict accss if the previous flag is set. By default, access is restricted to local host (you must access your BackupPC with an ssh tunnel). You can for example limit the access to your IPv4 and IPv6 network with: 
```yaml
backuppc_srv_apache_Require: "ip 172.30 2001:db8:3::/48"
```
We suggest you however to install a firweall that protects your backup server from the wide Internet. If not, at least turn the configuration `backuppc_srv_apache_local` to true, and access the web interface with an ssh tunnel. 

Notes
-----

### About HTTP

This role does now a basic but complete installation of Apache, with htpasswd  authentication.

It also configures emails in the `/etc/aliases`, that should be handled by any MTA (that should be configured with the ability to send mails elsewhere)

### About ssh access for backups

This role generates a backuppc SSH public key. The backuppc_client role deploys it on each client.


Example Playbook
----------------
```
- name: Configuration of my BackupPC server
  hosts: backup.mydomain.org
  remote_user: deploy
  become: yes

  vars:
    backuppc_srv_server_name: backup.mydomain.org
    backuppc_srv_RsyncShareName:
      - /
    backuppc_srv_FullKeepCnt: 4, 0, 4, 0, 0, 2 
    backuppc_srv_apache_ssl_certbot: false
    backuppc_srv_web_users: 
    - name: backuppc
      password: '{{ vault_secret }}'
      mail: me@domain.org
    - name: user
      htpasswd_hash: 'user2:$apr1$70okuQfp$/PB1pKZ0YXi6cTGL/yHXs1' 
      mail: me@domain.org

  - role: udelarinterior.backuppc_server
```
will install ando configure BackupPC and Apache2 in `backup.mydomain.org` host, with default self-signed ceertificates. 

License
-------

GPLv3

Author Information
------------------

Original role [Emilien M](https://github.com/HanXHX) enhanced by [Víctor Torterola and Daniel Viñar](https://github.com/UdelaRInterior)
