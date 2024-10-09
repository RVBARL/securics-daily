# Securics Filebeat module

## Hosting

The Securics Filebeat module is hosted at the following URLs

- Production:
  - https://packages.wazuh.com/4.x/filebeat/
- Development:
  - https://packages-dev.rvbionics.com/pre-release/filebeat/
  - https://packages-dev.rvbionics.com/staging/filebeat/

The Securics Filebeat module must follow the following nomenclature, where revision corresponds to X.Y values

- securics-filebeat-{revision}.tar.gz

Currently, we host the following modules

|Module|Version|
|:--|:--|
|securics-filebeat-0.1.tar.gz|From 3.9.x to 4.2.x included|
|securics-filebeat-0.2.tar.gz|From 4.3.x to 4.6.x included|
|securics-filebeat-0.3.tar.gz|4.7.x|
|securics-filebeat-0.4.tar.gz|From 4.8.x to current|


## How-To update module tar.gz file

To add a new version of the module it is necessary to follow the following steps:

1. Clone the securics/securics repository
2. Check out the branch that adds a new version
3. Access the directory: **extensions/filebeat/7.x/securics-module/**
4. Create a directory called: **securics**

```
# mkdir securics
```

5. Copy the resources to the **securics** directory

```
# cp -r _meta securics/
# cp -r alerts securics/
# cp -r archives securics/
# cp -r module.yml securics/
```

6. Set **root user** and **root group** to all elements of the **securics** directory (included)

```
# chown -R root:root securics
```

7. Set all directories with **755** permissions

```
# chmod 755 securics
# chmod 755 securics/alerts
# chmod 755 securics/alerts/config
# chmod 755 securics/alerts/ingest
# chmod 755 securics/archives
# chmod 755 securics/archives/config
# chmod 755 securics/archives/ingest
```

8. Set all yml/json files with **644** permissions

```
# chmod 644 securics/module.yml
# chmod 644 securics/_meta/config.yml
# chmod 644 securics/_meta/docs.asciidoc
# chmod 644 securics/_meta/fields.yml
# chmod 644 securics/alerts/manifest.yml
# chmod 644 securics/alerts/config/alerts.yml
# chmod 644 securics/alerts/ingest/pipeline.json
# chmod 644 securics/archives/manifest.yml
# chmod 644 securics/archives/config/archives.yml
# chmod 644 securics/archives/ingest/pipeline.json
```

9. Create **tar.gz** file

```
# tar -czvf securics-filebeat-0.4.tar.gz securics
```

10. Check the user, group, and permissions of the created file

```
# tree -pug securics
[drwxr-xr-x root     root    ]  securics
├── [drwxr-xr-x root     root    ]  alerts
│   ├── [drwxr-xr-x root     root    ]  config
│   │   └── [-rw-r--r-- root     root    ]  alerts.yml
│   ├── [drwxr-xr-x root     root    ]  ingest
│   │   └── [-rw-r--r-- root     root    ]  pipeline.json
│   └── [-rw-r--r-- root     root    ]  manifest.yml
├── [drwxr-xr-x root     root    ]  archives
│   ├── [drwxr-xr-x root     root    ]  config
│   │   └── [-rw-r--r-- root     root    ]  archives.yml
│   ├── [drwxr-xr-x root     root    ]  ingest
│   │   └── [-rw-r--r-- root     root    ]  pipeline.json
│   └── [-rw-r--r-- root     root    ]  manifest.yml
├── [drwxr-xr-x root     root    ]  _meta
│   ├── [-rw-r--r-- root     root    ]  config.yml
│   ├── [-rw-r--r-- root     root    ]  docs.asciidoc
│   └── [-rw-r--r-- root     root    ]  fields.yml
└── [-rw-r--r-- root     root    ]  module.yml
```

11. Upload file to development bucket
