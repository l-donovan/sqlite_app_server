# SQLite App Server

Inspired by [SQLite as an Application File Format](https://www.sqlite.org/appfileformat.html)

Entire webpages are stored in a single SQLite database. HTML files can link to other files stored locally in the same database. In its current iteration, only plain text files are stored, although this should be extensible to allow for any file format. A Python class, `AppFileServer`, hosts a local server on a specified port that serves files stored in a given database. Utility functions `tools.db_create` and `tools.db_verify` are provided for convenience.