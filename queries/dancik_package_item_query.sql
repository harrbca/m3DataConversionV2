select icompo,
       IWIDTH,
       IPACCD,
       "IIM#1" as UMF_1,
       "IIM11@" as UM1_1,
       "IIM21@" as UM2_1,

       "IIM#2" as UMF_2,
       "IIM12@" as UM1_2,
       "IIM22@" as UM2_2,

       "IIM#2" as UMF_3,
       "IIM13@" as UM1_3,
       "IIM23@" as UM2_3,

       "IIM#4" as UMF_4,
       "IIM14@" as UM1_4,
       "IIM24@" as UM2_4,

       "IIM#5" as UMF_5,
       "IIM15@" as UM1_5,
       "IIM25@" as UM2_5,

       "IIM#6" as UMF_6,
       "IIM16@" as UM1_6,
       "IIM26@" as UM2_6

 from dancik_items where itemNumber = ?
