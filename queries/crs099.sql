select imfgr || "LPROD#" as prodLine, min(lname) as lname from dancik_items
    group by prodLine
    order by prodLine