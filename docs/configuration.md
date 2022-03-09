# Configuration
Kemono, as of version 3.0, uses a single JSON file for configuration. This file lists all configuration options, their types, and descriptions of their purpose/behavior. 

## Notes
- Kemono expects the configuration to be located in `config.json`, at the root of the repository. You may instruct the software to use another location by specifying the environment variable `KEMONO_CONFIG`.
- Kemono is forgiving and flexible by design, and will usually fill in the blanks with reasonable defaults if something is missing from your config. However, you are strongly advised to keep your config up-to-date to prevent unexpected behavior.

## Table of contents
- [General](#general)
- [Webserver](#webserver)
- [Archiver](#archiver)
- [Database](#database)
- [Redis](#redis)

<!--- https://jakebathman.github.io/Markdown-Table-Generator/ --->

## General
<!---
Key	Type	Description
`site`	String	The URL at which your instance will reside.
`development_mode`	Boolean	If `true`, this instance will run in development mode, enabling certain niceties like hot reloading. This should be disabled in production instances.
`download_directory`	String	The directory the webserver will serve files from, and the one the archiver will download to.
--->
**Key**|**Type**|**Description**
:-----:|:-----:|:-----:
`site`|String|The URL at which your instance will reside.
`development\_mode`|Boolean|If `true`, this instance will run in development mode, enabling certain niceties like hot reloading. This should be disabled in production instances.
`download\_directory`|String|The directory the webserver will serve files from, and the one the archiver will download to.

## Webserver
<!---
Key	Type	Description
`enabled`	Boolean	If `true`, the webserver will be enabled.
`secret_key`	String	The encryption key that will be used for session cookies. Make sure to make it random, secure, and reasonably long.
`workers`	Integer	The number of threads the webserver will use.
--->
**Key**|**Type**|**Description**
:-----:|:-----:|:-----:
`enabled`|Boolean|If `true`, the webserver will be enabled.
`secret\_key`|String|The encryption key that will be used for session cookies. Make sure to make it random, secure, and reasonably long.
`workers`|Integer|The number of threads the webserver will use.

## Archiver
<!---
Key	Type	Description
`enabled`	Boolean	If `true`, the archiver will be enabled.
`proxies`	Array of strings	If the array is not empty, the proxy URLs specified will be used at random for downloads and API calls. Tested to work with HTTP and SOCKS5 - other protocols might work, maybe?
`ban_prefix`	String	If a prefix URL (example: `http://10.0.0.1:8313`) is specified, the archiver will send HTTP `BAN` requests towards it as needed to clear caches, ensuring updates are visible on the frontend. 
`public_key`	String	Public RSA encryption key for auto-imports and debug contributions. Assuming you have OpenSSL installed, a new key can be generated with the command `openssl genrsa -out privatekey.txt 4096 && openssl rsa -in privatekey.txt -pubout -out publickey && cat publickey`. Using 4096-bit keys are recommended.
`salt`	String	A static salt used during auto-import to hash keys. Set it to a secure string once and never again, or you will begin to encounter issues.
`queue_limit`	Integer	The maximum amount of imports that can run at once.
--->
**Key**|**Type**|**Description**
:-----:|:-----:|:-----:
`enabled`|Boolean|If `true`, the archiver will be enabled.
`proxies`|Array of strings|If the array is not empty, the proxy URLs specified will be used at random for downloads and API calls. Tested to work with HTTP and SOCKS5 - other protocols might work, maybe?
`ban\_prefix`|String|If a prefix URL (example: `http://10.0.0.1:8313`) is specified, the archiver will send HTTP `BAN` requests towards it as needed to clear caches, ensuring updates are visible on the frontend. 
`public\_key`|String|Public RSA encryption key for auto-imports and debug contributions. Assuming you have OpenSSL installed, a new key can be generated with the command `openssl genrsa -out privatekey.txt 4096 && openssl rsa -in privatekey.txt -pubout -out publickey && cat publickey`. Using 4096-bit keys are recommended.
`salt`|String|A static salt used during auto-import to hash keys. Set it to a secure string once and never again, or you will begin to encounter issues.
`queue\_limit`|Integer|The maximum amount of imports that can run at once.

## Database
<!---
Key	Type	Description
`host`	String	The host the PostgreSQL server is located at.
`user`	String	The PostgreSQL user that should be used during login.
`password`	String	The PostgreSQL password that should be used during login.
`database`	String	The PostgreSQL database that data will be stored to and retrieved from.
`port`	Integer	The port the PostgreSQL server is located at.
--->
**Key**|**Type**|**Description**
:-----:|:-----:|:-----:
`host`|String|The host the PostgreSQL server is located at.
`user`|String|The PostgreSQL user that should be used during login.
`password`|String|The PostgreSQL password that should be used during login.
`database`|String|The PostgreSQL database that data will be stored to and retrieved from.
`port`|Integer|The port the PostgreSQL server is located at.

## Redis
Kemono is designed to be capable of connecting to multiple Redis servers for improved performance. Different types of data are mapped to different nodes. By default though, the configuration simply uses one. `defaults` is all you need to worry about. Changing nodes and keyspaces is not recommended for the inexperienced.

<!---
Key	Type	Description
`defaults`	Dictionary	The settings specified here will be applied to all `nodes`.
`defaults -> host`	String	The host the Redis server is running at.
`defaults -> port`	Integer	The database that should be used.
`nodes`	Array of dictionaries	The nodes.
`keyspaces`	Dictionary	Key prefix -> Node mappings.
--->
**Key**|**Type**|**Description**
:-----:|:-----:|:-----:
`defaults`|Dictionary|The settings specified here will be applied to all `nodes`.
`defaults -> host`|String|The host the Redis server is running at.
`defaults -> port`|Integer|The database that should be used.
`nodes`|Array of dictionaries|The nodes.
`keyspaces`|Dictionary|Key prefix -> Node mappings.