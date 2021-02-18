# hca-util release notes

## 18 February 2021 v0.2.15
- Bug fix
  - Fix assignment of dcp-type=data content-type when syncing files to the submission upload area

## 15 January 2021 v0.2.14
- Improvement
  - handle delete command access denied exception

## 15 January 2021 v0.2.13
- Bug fix
  - issue [#372](https://github.com/ebi-ait/hca-ebi-dev-team/issues/372)
  - include changes on how permissions are assigned for new upload areas
- Other
  - notify when new version available

## 18 August 2020 v0.2.12
- Other
  - added default content-type when it can't be determined

## 12 August 2020 v0.2.11
- Bug fix
  - issue [#269](https://github.com/ebi-ait/hca-ebi-dev-team/issues/269)

## 29 July 2020 v0.2.10
- Improvement
  - sync command optimisation

## 28 July 2020 v0.2.9
- Bug fix
  - missing dependency

## 23 July 2020 v0.2.8
- Bug fixes
  - issue [#233](https://github.com/ebi-ait/hca-ebi-dev-team/issues/233) 
- Refactoring
  - addressed issue with individual file progress. New overall progress bar
  - use threadpool instead of threading in sync command
  - moved upload service methods in separate module

## 20 July 2020 v0.2.7
- Bug fixes
  - handle no labels exception
  - missing requests dep pkg
- Other
  - enforced min python version 3.6