import json

from app.client.engsel import get_family, get_package_details
from app.menus.package import show_package_details
from app.service.auth import AuthInstance
from app.menus.util import clear_screen, format_quota_byte, pause, display_html
from app.client.purchase.ewallet import show_multipayment
from app.client.purchase.qris import show_qris_payment
from app.client.purchase.balance import settlement_balance
from app.type_dict import PaymentItem

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

WIDTH = 55

def show_hot_menu():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        print(f"{bcolors.HEADER}{bcolors.BOLD}{'=' * WIDTH}{bcolors.ENDC}")
        print(f"{bcolors.HEADER}{bcolors.BOLD}{'🔥 Paket Hot 🔥'.center(WIDTH)}{bcolors.ENDC}")
        print(f"{bcolors.HEADER}{bcolors.BOLD}{'=' * WIDTH}{bcolors.ENDC}")
        
        hot_packages = []
        
        with open("hot_data/hot.json", "r", encoding="utf-8") as f:
            hot_packages = json.load(f)

        for idx, p in enumerate(hot_packages):
            print(f"{bcolors.OKCYAN}{idx + 1}.{bcolors.ENDC} {p['family_name']} - {p['variant_name']} - {p['option_name']}")
            print(f"{bcolors.OKBLUE}{'-' * WIDTH}{bcolors.ENDC}")
        
        print(f"{bcolors.WARNING}00. Kembali ke menu utama{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}{'-' * WIDTH}{bcolors.ENDC}")
        choice = input(f"{bcolors.BOLD}Pilih paket (nomor): {bcolors.ENDC}")
        if choice == "00":
            in_bookmark_menu = False
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_bm = hot_packages[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]
            
            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                print(f"{bcolors.FAIL}Gagal mengambil data family.{bcolors.ENDC}")
                pause()
                continue
            
            package_variants = family_data["package_variants"]
            option_code = None
            for variant in package_variants:
                if variant["name"] == selected_bm["variant_name"]:
                    selected_variant = variant
                    
                    package_options = selected_variant["package_options"]
                    for option in package_options:
                        if option["order"] == selected_bm["order"]:
                            selected_option = option
                            option_code = selected_option["package_option_code"]
                            break
            
            if option_code:
                print(f"{bcolors.OKGREEN}Option Code: {option_code}{bcolors.ENDC}")
                show_package_details(api_key, tokens, option_code, is_enterprise)            
            
        else:
            print(f"{bcolors.FAIL}Input tidak valid. Silahkan coba lagi.{bcolors.ENDC}")
            pause()
            continue

def show_hot_menu2():
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        main_package_detail = {}
        print(f"{bcolors.HEADER}{bcolors.BOLD}{'=' * WIDTH}{bcolors.ENDC}")
        print(f"{bcolors.HEADER}{bcolors.BOLD}{'🔥 Paket Hot 2 🔥'.center(WIDTH)}{bcolors.ENDC}")
        print(f"{bcolors.HEADER}{bcolors.BOLD}{'=' * WIDTH}{bcolors.ENDC}")
        
        hot_packages = []
        
        with open("hot_data/hot2.json", "r", encoding="utf-8") as f:
            hot_packages = json.load(f)

        for idx, p in enumerate(hot_packages):
            print(f"{bcolors.OKCYAN}{idx + 1}. {p['name']}{bcolors.ENDC}\n   Harga: {bcolors.OKGREEN}{p['price']}{bcolors.ENDC}")
            print(f"{bcolors.OKBLUE}{'-' * WIDTH}{bcolors.ENDC}")
        
        print(f"{bcolors.WARNING}00. Kembali ke menu utama{bcolors.ENDC}")
        print(f"{bcolors.OKBLUE}{'-' * WIDTH}{bcolors.ENDC}")
        choice = input(f"{bcolors.BOLD}Pilih paket (nomor): {bcolors.ENDC}")
        if choice == "00":
            in_bookmark_menu = False
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_package = hot_packages[int(choice) - 1]
            packages = selected_package.get("packages", [])
            if len(packages) == 0:
                print(f"{bcolors.FAIL}Paket tidak tersedia.{bcolors.ENDC}")
                pause()
                continue
            
            payment_items = []
            for package in packages:
                package_detail = get_package_details(
                    api_key,
                    tokens,
                    package["family_code"],
                    package["variant_code"],
                    package["order"],
                    package["is_enterprise"],
                    package["migration_type"],
                )
                
                if package == packages[0]:
                    main_package_detail = package_detail
                
                if not package_detail:
                    print(f"{bcolors.FAIL}Gagal mengambil detail paket untuk {package['family_code']}.{bcolors.ENDC}")
                    return None
                
                payment_items.append(
                    PaymentItem(
                        item_code=package_detail["package_option"]["package_option_code"],
                        product_type="",
                        item_price=package_detail["package_option"]["price"],
                        item_name=package_detail["package_option"]["name"],
                        tax=0,
                        token_confirmation=package_detail["token_confirmation"],
                    )
                )
            
            clear_screen()
            print(f"{bcolors.HEADER}{'=' * WIDTH}{bcolors.ENDC}")
            print(f"{bcolors.BOLD}Name: {selected_package['name']}{bcolors.ENDC}")
            print(f"Price: {bcolors.OKGREEN}{selected_package['price']}{bcolors.ENDC}")
            print(f"Detail: {selected_package['detail']}")
            print(f"{bcolors.HEADER}{'=' * WIDTH}{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN}{'Main Package Details:'.center(WIDTH)}{bcolors.ENDC}")
            print("-" * WIDTH)
            
            price = main_package_detail["package_option"]["price"]
            detail = display_html(main_package_detail["package_option"]["tnc"])
            validity = main_package_detail["package_option"]["validity"]

            option_name = main_package_detail.get("package_option", {}).get("name","")
            family_name = main_package_detail.get("package_family", {}).get("name","")
            variant_name = main_package_detail.get("package_detail_variant", {}).get("name","")
            
            title = f"{family_name} - {variant_name} - {option_name}".strip()
            
            family_code = main_package_detail.get("package_family", {}).get("package_family_code","")
            parent_code = main_package_detail.get("package_addon", {}).get("parent_code","")
            if parent_code == "":
                parent_code = "N/A"
            
            payment_for = main_package_detail["package_family"]["payment_for"]
                
            print(f"Nama: {bcolors.BOLD}{title}{bcolors.ENDC}")
            print(f"Harga: {bcolors.OKGREEN}Rp {price}{bcolors.ENDC}")
            print(f"Payment For: {payment_for}")
            print(f"Masa Aktif: {validity}")
            print(f"Point: {main_package_detail['package_option']['point']}")
            print(f"Plan Type: {main_package_detail['package_family']['plan_type']}")
            print("-" * WIDTH)
            print(f"Family Code: {bcolors.OKBLUE}{family_code}{bcolors.ENDC}")
            print(f"Parent Code: {parent_code}")
            print("-" * WIDTH)
            
            benefits = main_package_detail["package_option"]["benefits"]
            if benefits and isinstance(benefits, list):
                print(f"{bcolors.OKCYAN}Benefits:{bcolors.ENDC}")
                for benefit in benefits:
                    print("-" * WIDTH)
                    print(f" Name: {benefit['name']}")
                    data_type = benefit['data_type']
                    if data_type == "VOICE" and benefit['total'] > 0:
                        print(f"  Total: {benefit['total']/60} menit")
                    elif data_type == "TEXT" and benefit['total'] > 0:
                        print(f"  Total: {benefit['total']} SMS")
                    elif data_type == "DATA" and benefit['total'] > 0:
                        quota_formatted = format_quota_byte(int(benefit['total']))
                        print(f"  Total: {bcolors.OKGREEN}{quota_formatted}{bcolors.ENDC} ({data_type})")
                    
                    if benefit["is_unlimited"]:
                        print(f"  Unlimited: {bcolors.OKGREEN}Yes{bcolors.ENDC}")

            print("-" * WIDTH)
            print(f"{bcolors.WARNING}SnK MyXL:{bcolors.ENDC}\n{detail}")
            print(f"{bcolors.HEADER}{'=' * WIDTH}{bcolors.ENDC}")
            
            in_payment_menu = True
            while in_payment_menu:
                print(f"{bcolors.BOLD}Pilih Metode Pembelian:{bcolors.ENDC}")
                print("1. Balance")
                print("2. E-Wallet")
                print("3. QRIS")
                print(f"{bcolors.WARNING}00. Kembali ke menu sebelumnya{bcolors.ENDC}")
                
                input_method = input(f"{bcolors.BOLD}Pilih metode (nomor): {bcolors.ENDC}")
                if input_method == "1":
                    if selected_package.get("overwrite_amount", -1) == -1:
                        print(f"{bcolors.FAIL}{bcolors.BOLD}Pastikan sisa balance KURANG DARI Rp{payment_items[-1]['item_price']}!!!{bcolors.ENDC}")
                        balance_answer = input(f"{bcolors.WARNING}Yakin ingin melanjutkan? (y/n): {bcolors.ENDC}")
                        if balance_answer.lower() != "y":
                            print("Pembelian dibatalkan.")
                            pause()
                            in_payment_menu = False
                            continue

                    settlement_balance(api_key, tokens, payment_items, payment_for, 
                                       selected_package.get("ask_overwrite", False),
                                       overwrite_amount=selected_package.get("overwrite_amount", -1),
                                       token_confirmation_idx=selected_package.get("token_confirmation_idx", 0),
                                       amount_idx=selected_package.get("amount_idx", -1))
                    input(f"{bcolors.OKGREEN}Tekan enter untuk kembali...{bcolors.ENDC}")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "2":
                    show_multipayment(api_key, tokens, payment_items, payment_for, 
                                      selected_package.get("ask_overwrite", False),
                                      selected_package.get("overwrite_amount", -1),
                                      selected_package.get("token_confirmation_idx", 0),
                                      selected_package.get("amount_idx", -1))
                    input(f"{bcolors.OKGREEN}Tekan enter untuk kembali...{bcolors.ENDC}")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "3":
                    show_qris_payment(api_key, tokens, payment_items, payment_for, 
                                      selected_package.get("ask_overwrite", False),
                                      selected_package.get("overwrite_amount", -1),
                                      selected_package.get("token_confirmation_idx", 0),
                                      selected_package.get("amount_idx", -1))
                    input(f"{bcolors.OKGREEN}Tekan enter untuk kembali...{bcolors.ENDC}")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "00":
                    in_payment_menu = False
                else:
                    print(f"{bcolors.FAIL}Metode tidak valid.{bcolors.ENDC}")
                    pause()
        else:
            print(f"{bcolors.FAIL}Input tidak valid.{bcolors.ENDC}")
            pause()