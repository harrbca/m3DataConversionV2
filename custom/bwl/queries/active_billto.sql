select * from billto where
                         bname not like '*%' and
                         bacct > 9999 and
                         "BCO#" in ('0', '7') and
                         BBCOCD not in ('IA') and
                         BBRAN in ('CAL', 'EDM', 'WIN', 'SAS', 'REG', 'VAN', 'POR', 'SPO', 'TUK', 'ZSE', 'TOR')