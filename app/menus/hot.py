import requests

from app.colors import bcolors

WIDTH = 55
url2 = "https://api.baloenk.my.id"

def show_hot_menu():
    from app.client.engsel import get_family
    from app.menus.util import clear_screen, pause
    from app.service.auth import AuthInstance
    from app.menus.package import show_package_details
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
        print(f"{bcolors.BOLD}{bcolors.WARNING} Paket Hot {bcolors.ENDC}".center(WIDTH + 18))
        print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
        
        url = "https://api.baloenk.my.id/pg-hot.json"
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"{bcolors.FAIL} Gagal mengambil data hot package.{bcolors.ENDC}")
            pause()
            return None

        hot_packages = response.json()

        for idx, p in enumerate(hot_packages):
            print(f"{bcolors.OKCYAN}[{idx + 1:02d}]{bcolors.ENDC} {bcolors.BOLD}{p['family_name']}{bcolors.ENDC} {bcolors.WARNING}{bcolors.ENDC} {bcolors.OKGREEN}{p['variant_name']}{bcolors.ENDC} {bcolors.WARNING}{bcolors.ENDC} {bcolors.OKBLUE}{p['option_name']}{bcolors.ENDC}")
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
        
        print(f"{bcolors.FAIL}[00]{bcolors.ENDC} {bcolors.OKCYAN} Kembali ke menu utama{bcolors.ENDC}")
        print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
        choice = input(f"{bcolors.BOLD} Pilih paket (nomor): {bcolors.ENDC}")
        if choice == "00":
            in_bookmark_menu = False
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_bm = hot_packages[int(choice) - 1]
            family_code = selected_bm["family_code"]
            is_enterprise = selected_bm["is_enterprise"]
            
            family_data = get_family(api_key, tokens, family_code, is_enterprise)
            if not family_data:
                print(f"{bcolors.FAIL} Gagal mengambil data family.{bcolors.ENDC}")
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
                print(f"{bcolors.OKGREEN} Option Code: {option_code}{bcolors.ENDC}")
                show_package_details(api_key, tokens, option_code, is_enterprise)            
            
        else:
            print(f"{bcolors.FAIL} Input tidak valid. Silahkan coba lagi.{bcolors.ENDC}")
            pause()
            continue

def show_hot_menu2():
    from app.client.engsel import get_package_details
    from app.menus.util import clear_screen, format_quota_byte, pause, display_html
    from app.client.purchase.ewallet import show_multipayment
    from app.client.purchase.qris import show_qris_payment
    from app.client.purchase.balance import settlement_balance
    from app.type_dict import PaymentItem
    from app.service.auth import AuthInstance
    api_key = AuthInstance.api_key
    tokens = AuthInstance.get_active_tokens()
    
    in_bookmark_menu = True
    while in_bookmark_menu:
        clear_screen()
        main_package_detail = {}
        print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
        print(f"{bcolors.BOLD}{bcolors.WARNING} Paket Hot 2 {bcolors.ENDC}".center(WIDTH + 18))
        print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
        
        url = "https://api.baloenk.my.id/pg-hot2.json"
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"{bcolors.FAIL} Gagal mengambil data hot package.{bcolors.ENDC}")
            pause()
            return None

        hot_packages = response.json()

        for idx, p in enumerate(hot_packages):
            print(f"{bcolors.OKCYAN}[{idx + 1:02d}]{bcolors.ENDC} {bcolors.BOLD}{p['name']}{bcolors.ENDC}")
            print(f"     {bcolors.WARNING} Harga:{bcolors.ENDC} {bcolors.OKGREEN}Rp {p['price']}{bcolors.ENDC}")
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
        
        print(f"{bcolors.FAIL}[00]{bcolors.ENDC} {bcolors.OKCYAN} Kembali ke menu utama{bcolors.ENDC}")
        print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
        choice = input(f"{bcolors.BOLD} Pilih paket (nomor): {bcolors.ENDC}")
        if choice == "00":
            in_bookmark_menu = False
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(hot_packages):
            selected_package = hot_packages[int(choice) - 1]
            packages = selected_package.get("packages", [])
            if len(packages) == 0:
                print(f"{bcolors.WARNING} Paket tidak tersedia.{bcolors.ENDC}")
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
                
                # Force failed when one of the package detail is None
                if not package_detail:
                    print(f"{bcolors.FAIL} Gagal mengambil detail paket untuk {package['family_code']}.{bcolors.ENDC}")
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
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN} Name:{bcolors.ENDC} {bcolors.BOLD}{selected_package['name']}{bcolors.ENDC}")
            print(f"{bcolors.WARNING} Price:{bcolors.ENDC} {bcolors.OKGREEN}Rp {selected_package['price']}{bcolors.ENDC}")
            print(f"{bcolors.OKBLUE} Detail:{bcolors.ENDC} {selected_package['detail']}")
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
            print(f"{bcolors.BOLD}{bcolors.OKCYAN} Main Package Details:{bcolors.ENDC}".center(WIDTH + 18))
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
            # Show package 0 details
            
            price = main_package_detail["package_option"]["price"]
            detail = display_html(main_package_detail["package_option"]["tnc"])
            validity = main_package_detail["package_option"]["validity"]

            option_name = main_package_detail.get("package_option", {}).get("name","") #Vidio
            family_name = main_package_detail.get("package_family", {}).get("name","") #Unlimited Turbo
            variant_name = main_package_detail.get("package_detail_variant", "").get("name","") #For Xtra Combo
            option_name = main_package_detail.get("package_option", {}).get("name","") #Vidio
            
            title = f"{family_name} - {variant_name} - {option_name}".strip()
            
            family_code = main_package_detail.get("package_family", {}).get("package_family_code","")
            parent_code = main_package_detail.get("package_addon", {}).get("parent_code","")
            if parent_code == "":
                parent_code = "N/A"
            
            payment_for = main_package_detail["package_family"]["payment_for"]
                
            print(f"{bcolors.OKCYAN} Nama:{bcolors.ENDC} {bcolors.BOLD}{title}{bcolors.ENDC}")
            print(f"{bcolors.WARNING} Harga:{bcolors.ENDC} {bcolors.OKGREEN}Rp {price}{bcolors.ENDC}")
            print(f"{bcolors.OKBLUE} Payment For:{bcolors.ENDC} {bcolors.BOLD}{payment_for}{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN} Masa Aktif:{bcolors.ENDC} {bcolors.OKGREEN}{validity} hari{bcolors.ENDC}")
            print(f"{bcolors.WARNING} Point:{bcolors.ENDC} {bcolors.BOLD}{main_package_detail['package_option']['point']}{bcolors.ENDC}")
            print(f"{bcolors.OKBLUE} Plan Type:{bcolors.ENDC} {bcolors.BOLD}{main_package_detail['package_family']['plan_type']}{bcolors.ENDC}")
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN} Family Code:{bcolors.ENDC} {bcolors.BOLD}{family_code}{bcolors.ENDC}")
            print(f"{bcolors.WARNING} Parent Code (for addon/dummy):{bcolors.ENDC} {bcolors.BOLD}{parent_code}{bcolors.ENDC}")
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
            benefits = main_package_detail["package_option"]["benefits"]
            if benefits and isinstance(benefits, list):
                print(f"{bcolors.BOLD}{bcolors.OKGREEN} Benefits:{bcolors.ENDC}")
                for benefit in benefits:
                    print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
                    print(f" {bcolors.OKCYAN} Name:{bcolors.ENDC} {bcolors.BOLD}{benefit['name']}{bcolors.ENDC}")
                    print(f"  {bcolors.OKBLUE} Item id:{bcolors.ENDC} {benefit['item_id']}")
                    data_type = benefit['data_type']
                    if data_type == "VOICE" and benefit['total'] > 0:
                        print(f"  {bcolors.WARNING} Total:{bcolors.ENDC} {bcolors.OKGREEN}{benefit['total']/60} menit{bcolors.ENDC}")
                    elif data_type == "TEXT" and benefit['total'] > 0:
                        print(f"  {bcolors.WARNING} Total:{bcolors.ENDC} {bcolors.OKGREEN}{benefit['total']} SMS{bcolors.ENDC}")
                    elif data_type == "DATA" and benefit['total'] > 0:
                        if benefit['total'] > 0:
                            quota = int(benefit['total'])
                            quota_formatted = format_quota_byte(quota)
                            print(f"  {bcolors.WARNING} Total:{bcolors.ENDC} {bcolors.OKGREEN}{quota_formatted}{bcolors.ENDC} ({bcolors.OKBLUE}{data_type}{bcolors.ENDC})")
                    elif data_type not in ["DATA", "VOICE", "TEXT"]:
                        print(f"  {bcolors.WARNING} Total:{bcolors.ENDC} {bcolors.OKGREEN}{benefit['total']}{bcolors.ENDC} ({bcolors.OKBLUE}{data_type}{bcolors.ENDC})")
                    
                    if benefit["is_unlimited"]:
                        print(f"  {bcolors.BOLD} Unlimited:{bcolors.ENDC} {bcolors.OKGREEN}Yes {bcolors.ENDC}")

            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
            print(f"{bcolors.BOLD}{bcolors.OKCYAN} SnK MyXL:{bcolors.ENDC}\n{detail}")
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
                
            print(f"{bcolors.HEADER}{'' * WIDTH}{bcolors.ENDC}")
            
            payment_for = selected_package.get("payment_for", "BUY_PACKAGE")
            ask_overwrite = selected_package.get("ask_overwrite", False)
            overwrite_amount = selected_package.get("overwrite_amount", -1)
            token_confirmation_idx = selected_package.get("token_confirmation_idx", 0)
            amount_idx = selected_package.get("amount_idx", -1)

            in_payment_menu = True
            while in_payment_menu:
                print(f"\n{bcolors.BOLD}{bcolors.OKCYAN} Pilih Metode Pembelian:{bcolors.ENDC}")
                print(f"{bcolors.OKGREEN}[1]{bcolors.ENDC}  Balance")
                print(f"{bcolors.OKGREEN}[2]{bcolors.ENDC}  E-Wallet")
                print(f"{bcolors.OKGREEN}[3]{bcolors.ENDC}  QRIS")
                print(f"{bcolors.FAIL}[00]{bcolors.ENDC} {bcolors.OKCYAN} Kembali ke menu sebelumnya{bcolors.ENDC}")
                
                input_method = input(f"\n{bcolors.BOLD} Pilih metode (nomor): {bcolors.ENDC}")
                if input_method == "1":
                    if overwrite_amount == -1:
                        print(f"{bcolors.WARNING} Pastikan sisa balance KURANG DARI Rp{payment_items[-1]['item_price']}!!!{bcolors.ENDC}")
                        balance_answer = input(f"{bcolors.BOLD} Apakah anda yakin ingin melanjutkan pembelian? (y/n): {bcolors.ENDC}")
                        if balance_answer.lower() != "y":
                            print(f"{bcolors.WARNING} Pembelian dibatalkan oleh user.{bcolors.ENDC}")
                            pause()
                            in_payment_menu = False
                            continue

                    settlement_balance(
                        api_key,
                        tokens,
                        payment_items,
                        payment_for,
                        ask_overwrite,
                        overwrite_amount=overwrite_amount,
                        token_confirmation_idx=token_confirmation_idx,
                        amount_idx=amount_idx,
                    )
                    input(f"{bcolors.OKCYAN} Tekan enter untuk kembali...{bcolors.ENDC}")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "2":
                    show_multipayment(
                        api_key,
                        tokens,
                        payment_items,
                        payment_for,
                        ask_overwrite,
                        overwrite_amount,
                        token_confirmation_idx,
                        amount_idx,
                    )
                    input(f"{bcolors.OKCYAN} Tekan enter untuk kembali...{bcolors.ENDC}")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "3":
                    show_qris_payment(
                        api_key,
                        tokens,
                        payment_items,
                        payment_for,
                        ask_overwrite,
                        overwrite_amount,
                        token_confirmation_idx,
                        amount_idx,
                    )

                    input(f"{bcolors.OKCYAN} Tekan enter untuk kembali...{bcolors.ENDC}")
                    in_payment_menu = False
                    in_bookmark_menu = False
                elif input_method == "00":
                    in_payment_menu = False
                    continue
                else:
                    print(f"{bcolors.FAIL} Metode tidak valid. Silahkan coba lagi.{bcolors.ENDC}")
                    pause()
                    continue
        else:
            print(f"{bcolors.FAIL} Input tidak valid. Silahkan coba lagi.{bcolors.ENDC}")
            pause()
            continue