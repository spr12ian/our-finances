row = [
    "2023-04-24",
    "SJL3BH",
    "MANAGEMENT FEE",
    "",
    69.00,
    "HMRC S UKP expense: legal, management an",
]
max_description_width = 40
max_category_width = 40

formatted_row = f"{row[0]} | {row[1]} | {row[2][:max_description_width]:<30} | {row[3]:<5} | {row[4]:>10.2f} | {row[5][:max_category_width]:<20}"
print(formatted_row)
