"""
Script para otimizar fotos do portfolio (reduzir peso do site).

O que ele faz:
- Le todas as imagens (.jpg, .jpeg, .png, .JPG, .JPEG, .PNG) da pasta atual
- Redimensiona para no maximo LARGURA_MAX de largura (mantem proporcao)
- Converte para .webp com qualidade QUALIDADE
- Salva tudo numa pasta nova "otimizadas" (nao mexe nos arquivos originais)

Como usar:
1. Instale as dependencias (uma vez so):
   pip install Pillow

2. Coloque este arquivo dentro da pasta "zoza" (mesma pasta das fotos)

3. Rode no terminal:
   python otimizar_imagens.py

4. As novas imagens vao aparecer em zoza/otimizadas/
   Depois e so trocar os caminhos no seu HTML (ex: "new balance.JPG" -> "otimizadas/new-balance.webp")
"""

import os
from pathlib import Path
from PIL import Image

# ===================== CONFIGURACOES =====================
LARGURA_MAX = 1800      # largura maxima em pixels (fotos maiores serao reduzidas)
QUALIDADE = 80           # qualidade do webp (0-100). 75-85 e um bom equilibrio
PASTA_ORIGEM = "."       # pasta onde estao as fotos originais
PASTA_DESTINO = "otimizadas"
EXTENSOES = {".jpg", ".jpeg", ".png"}
# ===========================================================


def formatar_tamanho(bytes_num):
    for unidade in ["B", "KB", "MB", "GB"]:
        if bytes_num < 1024:
            return f"{bytes_num:.1f}{unidade}"
        bytes_num /= 1024
    return f"{bytes_num:.1f}TB"


def nome_limpo(nome_arquivo):
    """Troca espacos por hifen e deixa tudo minusculo, ex: 'new balance.JPG' -> 'new-balance.webp'"""
    nome_sem_ext = os.path.splitext(nome_arquivo)[0]
    nome = nome_sem_ext.strip().lower().replace(" ", "-")
    return f"{nome}.webp"


def otimizar_imagens():
    origem = Path(PASTA_ORIGEM)
    destino = Path(PASTA_DESTINO)
    destino.mkdir(exist_ok=True)

    arquivos = [
        f for f in origem.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSOES
    ]

    if not arquivos:
        print("Nenhuma imagem encontrada nesta pasta.")
        return

    total_original = 0
    total_novo = 0
    convertidos = []

    print(f"Encontradas {len(arquivos)} imagens. Iniciando otimizacao...\n")

    for arquivo in arquivos:
        try:
            tamanho_original = arquivo.stat().st_size
            total_original += tamanho_original

            with Image.open(arquivo) as img:
                # Corrige orientacao de fotos tiradas com celular/camera
                try:
                    from PIL import ImageOps
                    img = ImageOps.exif_transpose(img)
                except Exception:
                    pass

                # Converte modo de cor se necessario (evita erro ao salvar webp)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")

                # Redimensiona mantendo proporcao, so se for maior que o limite
                if img.width > LARGURA_MAX:
                    nova_altura = int(img.height * (LARGURA_MAX / img.width))
                    img = img.resize((LARGURA_MAX, nova_altura), Image.LANCZOS)

                nome_saida = nome_limpo(arquivo.name)
                caminho_saida = destino / nome_saida

                img.save(caminho_saida, "WEBP", quality=QUALIDADE, method=6)

                tamanho_novo = caminho_saida.stat().st_size
                total_novo += tamanho_novo

                reducao = (1 - tamanho_novo / tamanho_original) * 100
                print(f"OK  {arquivo.name:35s} {formatar_tamanho(tamanho_original):>9s} -> {formatar_tamanho(tamanho_novo):>9s}  ({reducao:.0f}% menor)")
                convertidos.append((arquivo.name, nome_saida))

        except Exception as e:
            print(f"ERRO ao processar {arquivo.name}: {e}")

    print("\n" + "=" * 60)
    print(f"Total original: {formatar_tamanho(total_original)}")
    print(f"Total novo:     {formatar_tamanho(total_novo)}")
    if total_original > 0:
        print(f"Reducao total:  {(1 - total_novo / total_original) * 100:.0f}%")
    print(f"\nImagens salvas em: {destino.resolve()}")
    print("=" * 60)

    # Gera um arquivo de referencia mostrando nome antigo -> nome novo
    with open(destino / "mapa_de_nomes.txt", "w", encoding="utf-8") as f:
        f.write("Nome original -> Nome novo (use isso para atualizar o HTML)\n")
        f.write("-" * 60 + "\n")
        for antigo, novo in convertidos:
            f.write(f"{antigo}  ->  otimizadas/{novo}\n")

    print("\nUm arquivo 'mapa_de_nomes.txt' foi criado dentro de 'otimizadas/'")
    print("com a lista de nome antigo -> nome novo, pra te ajudar a atualizar o HTML.")


if __name__ == "__main__":
    otimizar_imagens()
