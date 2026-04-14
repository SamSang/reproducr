/*
Extract NIH grant numbers using a regular expression
*/
create table if not exists postgres.daan_822.grant as
with funds as (
	select
	pmid,
	jsonb_array_elements_text(funding::jsonb) as funding
	from postgres.daan_822.article_detailed
	where jsonb_array_length(funding::jsonb) > 0
),
nih as (
	select 
	pmid,
    regexp_replace(
        (regexp_matches(
            funding,
            E'(?<![A-Za-z0-9])((?:R|K|F|T|U|P)\\d{2}[ -]?[A-Z]{2}\\d{6})(?![A-Za-z0-9])',
            'g'
        ))[1],
        '[ -]',
        '',
        'g'
    ) AS nih_grant,
	funding
	from funds
)
select *
from nih;

/*
Extract DOI numbers from funding string using a regular expression
*/
create table if not exists postgres.daan_822.funder as
WITH funds AS (
    SELECT
        pmid,
        jsonb_array_elements_text(funding::jsonb) AS funding
    FROM postgres.daan_822.article_detailed
    WHERE jsonb_array_length(funding::jsonb) > 0
),
dois AS (
    SELECT
        pmid,
        (regexp_matches(
            funding,
            E'(10\.[0-9]{4,9}\/[^[:space:]A-Z]+)',
            'g'
        ))[1] AS doi,
        funding
    FROM funds
    WHERE funding ~
        E'10\\.\\d{4,9}/[^\\s"\'<>\\]]+'
)
SELECT *
FROM dois;