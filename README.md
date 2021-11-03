
konto
=====


A Python Library for Accounting.


konto is able to do basic accounting, generating sub-books from a main book.
Changes in the sub-books can be re-merged into the main book.

Additionally, there are tools to manipulate sub-books for different purposes:
Automatic assignment of contra account, computation of social insurance and
taxes for salaries, and other, are prepared.

konto is supposed to deal fast with big amounts of data.




1.  Basic functionality
=======================

1.1.  Base directory and acc-files
----------------------------------

To start an accounting, choose a directory and define a file which carries all
your bookings. The bookings have to have the following format:


    yyyymmdd    <amount>    <account>  <contra account>   <arbitrary amount>   <remark>


For example:

20211015    -30.67    10-B12-1802    13-7300   44.12   Zinszahlung und Kontogebuehr

First column is date, second the amount, third and fourth is account and contra account,
fifth is arbitray amount for consistence with the format of contributing so books, and
sixth column (here are spaces allowed as well) is a free remark.

It is mandatory that the first letter always is 2 in an account entry, so that every booking
has a date in the year range 2000..2999 !

The account entries in the third and fourth column define a hierarchy of accounts by
the - sign: 10-B12 is sub-account of 10, 10-B12-1802 is sub-account of 10-B12, and so on.

The standard name of the file is 2.acc, this means, all bookings in this file starts
with 2, It is also possible to have split off in more than one file, for example:

-   2019.acc
-   2020.acc
-   2021.acc

then all bookings starting with 2019 (bookings in the year 2019) find place in 2019.acc,
with 2020 (bookings in the year 2020) in 2020.acc, and so on.

Or you choose:

-   201.acc
-   202.acc

then all bookings of the decade 2010..2019 are in 201.acc, all of decade 2020..2029 in
202.acc, and so on.

You also can mix:

-   201.acc
-   2020.acc
-   2021.acc
-   2022.acc
    ....

but you must not (do not mix levels):

-   201.acc
-   2019.acc


Be aware that all acc-files are present for all the bookings you have in terms of date.


1.2.   The sum-files
--------------------

Each acc-file has an uniquely assigned sum-file of same file root (e,g, 201.acc -> 201.sum),
This file contains all monthly sums of all accounts and sub-accounts, for the sake of performance,
and has to be in synchronization with the acc-files.

All operations of konto keep this consistency. But in case you want to create the sum-files,
because the are lacking or not consistent anymore for some reason, do the following:

-   Delete all sum-files, if there are some.

-   python3 -m konto.base.konto 2 (1st run)

-   python3 -m konto.base.konto 2 (2nd run)


1.3.




