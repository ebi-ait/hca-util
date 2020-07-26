# hca-util release notes

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