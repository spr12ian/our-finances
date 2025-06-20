import finances.util.financial_helpers as uf
from helper_date_time import DateTimeHelper
from models import AccountBalances, BankAccounts, Transactions
from sqlalchemy import DECIMAL, cast, func, not_
from sqlalchemy_helper import SQLAlchemyHelper

sql = SQLAlchemyHelper()
session = sql.get_session()

query = (
    session.query(
        func.strftime("%Y-%m", Transactions.date).label("month"),
        func.sum(Transactions.credit).label("money_in"),
        func.sum(Transactions.debit).label("money_out"),
        func.sum(Transactions.credit - Transactions.debit).label("net_amount"),
    )
    .join(BankAccounts, BankAccounts.key == Transactions.key)
    .filter(
        BankAccounts.our_money == "TRUE",
        not_(Transactions.description.like("X%")),
        Transactions.date.between("2025-01-01", "2025-01-31"),
    )
    .group_by(func.strftime("%Y-%m", Transactions.date))
    .order_by("month")
)

print(query.statement.compile(compile_kwargs={"literal_binds": True}))

# Perform the query
results = query.all()
if len(results):
    # Print the results
    for result in results:
        print(f"type(result.money_in): {type(result.money_in)}")
        print(
            f"Month: {result.month}"
            + f", In: {uf.format_as_gbp(result.money_in, 11)}"
            + f", Out: {uf.format_as_gbp(result.money_out, 11)}"
            + f", Amount: {uf.format_as_gbp(result.net_amount, 11)}"
        )

query = (
    session.query(
        Transactions.date.label("transaction_date"),
        cast(Transactions.credit, DECIMAL).label("plus"),
        cast(Transactions.debit, DECIMAL).label("minus"),
        (cast(Transactions.credit, DECIMAL) - cast(Transactions.debit, DECIMAL)).label(
            "net"
        ),
        Transactions.description.label("description"),
    )
    .join(BankAccounts, BankAccounts.key == Transactions.key)
    .filter(
        BankAccounts.our_money == "TRUE",
        not_(Transactions.description.like("X%")),
        Transactions.date.between("2025-01-01", "2025-01-31"),
    )
    .order_by("transaction_date")
)

print(query.statement.compile(compile_kwargs={"literal_binds": True}))

# Perform the query
results = query.all()
if len(results):
    dth = DateTimeHelper()
    print("Date           Credit      Debit        Net Description")
    # Print the results
    for result in results:
        # Format the date as UK date (DD/MM/YYYY)
        date = result.transaction_date.strftime("%d/%m/%Y")
        plus = uf.format_as_gbp(result.plus, 11)
        minus = uf.format_as_gbp(result.minus, 11)
        net = uf.format_as_gbp(result.net, 11)
        description = result.description
        print(f"{date}{plus}{minus}{net} {description}")

query = (
    session.query(
        BankAccounts.key.label("key"),
        BankAccounts.our_money.label("our_money"),
        cast(AccountBalances.credit, DECIMAL).label("plus"),
        cast(AccountBalances.debit, DECIMAL).label("minus"),
        (
            cast(AccountBalances.credit, DECIMAL) - cast(AccountBalances.debit, DECIMAL)
        ).label("net"),
    )
    .join(BankAccounts, BankAccounts.key == AccountBalances.key)
    .filter(
        AccountBalances.credit != AccountBalances.debit,
    )
    .order_by("key")
)

print(query.statement.compile(compile_kwargs={"literal_binds": True}))

# Perform the query
results = query.all()
if len(results):
    dth = DateTimeHelper()
    print("Key    Our Money? Credit      Debit        Net")
    # Print the results
    for result in results:
        key = result.key
        our_money = result.our_money
        plus = uf.format_as_gbp(result.plus, 14)
        minus = uf.format_as_gbp(result.minus, 14)
        net = uf.format_as_gbp(result.net, 14)
        print(f"{key} {our_money}      {plus}{minus}{net}")


# account_balances = relationship("AccountBalances", back_populates="bank_accounts")
# bank_account = relationship("BankAccounts", back_populates="account_balances")

# # Query bank accounts and their account balances
# bank_accounts = session.query(BankAccounts).all()
# for account in bank_accounts:
#     print(f"Account: {account.full_account_name}")
#     for balance in account.account_balances:
#         print(
#             f"  Balance: Credit: {balance.credit}, Debit: {balance.debit}, Net: {balance.balance}"
#         )

# # Query account balances and their associated bank account
# account_balances = session.query(AccountBalances).all()
# for balance in account_balances:
#     print(
#         f"Balance: Credit: {balance.credit}, Debit: {balance.debit}, Net: {balance.balance}"
#     )
#     print(f"  Account: {balance.bank_account.full_account_name}")
