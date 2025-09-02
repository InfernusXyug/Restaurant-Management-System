from tabulate import tabulate
import mysql.connector as mc
import time

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "passwd": "1234",
    "database": "project"
}

ADMIN_PASSWORD = "*****"


# Utility: database connection
def get_connection():
    return mc.connect(**DB_CONFIG)


# Utility: execute a query (with optional fetch)
def run_query(query, fetch=False):
    con = get_connection()
    cur = con.cursor()
    cur.execute(query)
    result = cur.fetchall() if fetch else None
    con.commit()
    con.close()
    return result


# Item management
def add_item():
    n = int(input("Enter no. of records: "))
    for _ in range(n):
        ino = int(input("Enter the item no: "))
        iname = input("Enter the item name: ")
        iprice = int(input("Enter the item price: "))
        run_query(
            f"insert into hotel values({ino},'{iname}',{iprice})"
        )
    print("Items added successfully!\n")


def delete_item():
    n = int(input("Enter no. of records to delete: "))
    for _ in range(n):
        ino = int(input("Enter the item no: "))
        run_query(f"delete from hotel where ino={ino}")
    print("Items deleted successfully!\n")


def show_menu():
    data = run_query("select * from hotel", fetch=True)
    if not data:
        print("Menu is empty.")
        return
    headers = ['Code', 'Name', 'Price']
    print(tabulate(data, headers=headers, tablefmt='pretty'))


# Order management
def place_order():
    ch = 'y'
    while ch.lower() == 'y':
        ino = int(input("Enter item code -> "))
        data = run_query(f"select * from hotel where ino={ino}", fetch=True)
        if not data:
            print("Invalid item code.")
            return
        code, name, price = data[0]
        qty = int(input("Enter quantity: "))
        tot_amt = qty * price
        run_query(
            f"insert into item values({code},'{name}',{qty},{price},{tot_amt})"
        )
        ch = input("Do you want to add more? (y/n): ")


def cancel_order():
    adm_id = input("Enter the admin password: ")
    if adm_id == ADMIN_PASSWORD:
        run_query("drop table if exists item")
        print("Your order has been successfully cancelled!")
    else:
        print("Invalid admin password!")


# Billing & Reports
def billing():
    date = time.strftime("%d/%m/%Y")
    count = run_query("select count(*) from report", fetch=True)[0][0]
    billno = f"{date}-{count+1}"

    data = run_query("select * from item", fetch=True)
    if not data:
        print("No items to bill!")
        return

    headers = ['Code', 'Name', 'Qty', 'Price', 'Total']
    print(tabulate(data, headers=headers, tablefmt='outline'))

    total = run_query("select sum(tot_amount) from item", fetch=True)[0][0]
    print("\nTotal Amount:", total)
    print("\tTHANK YOU\n\tVisit Again!")

    run_query(f"insert into report values('{billno}',{total})")
    run_query("drop table if exists item")


def sales_report():
    data = run_query("select * from report", fetch=True)
    if not data:
        print("No sales recorded.")
        return
    headers = ['Bill No', 'Total Amount']
    print(tabulate(data, headers=headers, tablefmt='grid'))
    total = run_query("select sum(tot_amount) from report", fetch=True)[0][0]
    print("Total =", total)


# Main program
def admin_panel():
    passwd = input("Enter admin password: ")
    if passwd != ADMIN_PASSWORD:
        print("Invalid admin password!")
        return
    while True:
        choice = int(input("1.Add item\n2.Delete item\n3.Sales report\n4.Exit\nChoose: "))
        if choice == 1:
            add_item()
        elif choice == 2:
            delete_item()
        elif choice == 3:
            sales_report()
        elif choice == 4:
            break
        else:
            print("Invalid input!")


def customer_panel():
    show_menu()
    place_order()
    ch = int(input("1.Billing\n2.Cancel\nChoose: "))
    if ch == 1:
        billing()
    elif ch == 2:
        cancel_order()


def main():
    while True:
        print("\n--- Restaurant Management ---")
        choice = int(input("1.Admin login\n2.Customer login\n3.Exit\nChoose: "))
        if choice == 1:
            admin_panel()
        elif choice == 2:
            customer_panel()
        elif choice == 3:
            print("Exited from program.")
            break
        else:
            print("Invalid selection!")


if __name__ == "__main__":
    main()
