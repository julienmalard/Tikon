import डिब्बा

डिब्बा_शुरू = डिब्बा.डिब्बे.डिब्बा()

botón_inic = डिब्बा.botón()
botón_ayuda = डिब्बा.botón()

logo = डिब्बा.कला.चित्र('Logo_Tiko\'n')

डिब्बा_शुरू.जोड़ना(logo)

डिब्बा_शुरू.जोड़ना(botón_ayuda, texto='', acción='')
डिब्बा_शुरू.जोड़ना(botón_inic, texto='', acción=lambda: डिब्बा_शुरू.हटाना('उपर'))
