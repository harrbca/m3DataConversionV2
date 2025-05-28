WITH
    CombinedData as (
select 'BWL' as schemaName,
    W2WARE,
    W2AREA,
    W2DESC,
    W2BCODPRTF,
    W2BCODPRTQ,
    W2STAGEIN,
    W2STAGEOUT
FROM dancik_bwl.WM0002F

UNION ALL

select 'WAN' as schemaName,
    W2WARE,
    W2AREA,
    W2DESC,
    W2BCODPRTF,
    W2BCODPRTQ,
    W2STAGEIN,
    W2STAGEOUT
FROM dancik_wan.WM0002F
    )
select * from CombinedData