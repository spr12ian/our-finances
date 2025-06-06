import finances.util.financial_helpers as uf

print(uf.format_as_gbp(123456.789, 12))
print(uf.format_as_gbp(123.789, 12))
print(uf.format_as_gbp(123.789, 0))
