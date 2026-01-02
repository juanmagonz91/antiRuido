import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

class SourceNavigator:
    """
    Agente encargado de navegar a una URL, renderizar el JS (si es necesario)
    y extraer el texto limpio quirúrgicamente.
    """
    
    async def fetch_and_clean(self, url: str) -> dict:
        print(f"🌐 Navegando a: {url}")
        
        async with async_playwright() as p:
            # Lanzamos navegador headless (sin interfaz gráfica)
            browser = await p.chromium.launch(headless=True)
            
            # Contexto con User-Agent de usuario real para evitar bloqueos simples
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            try:
                # Timeout de 15 segundos para no colgar el proceso
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                # Obtenemos el HTML renderizado (útil para Single Page Apps)
                content_html = await page.content()
                
            except Exception as e:
                await browser.close()
                return {"error": f"Error de navegación: {str(e)}", "status": "failed"}
            
            await browser.close()

            # --- FASE DE LIMPIEZA (BeautifulSoup) ---
            soup = BeautifulSoup(content_html, "lxml")
            
            # 1. ELIMINACIÓN DE RUIDO ESTRUCTURAL
            # Eliminamos etiquetas que NUNCA tienen contenido relevante
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]):
                tag.decompose()

            # 2. EXTRACCIÓN DE METADATOS
            title = soup.title.string.strip() if soup.title else "Sin Título"
            
            # 3. EXTRACCIÓN DE TEXTO LIMPIO
            # get_text con separador asegura que los párrafos no se peguen
            text_content = soup.get_text(separator="\n", strip=True)
            
            # 4. LIMPIEZA POST-PROCESADO
            # Eliminamos líneas vacías múltiples
            lines = [line.strip() for line in text_content.splitlines() if line.strip()]
            clean_text = "\n".join(lines)
            
            # Retornamos estructura lista para el ContentScorer
            return {
                "status": "success",
                "url": url,
                "title": title,
                "clean_text": clean_text[:15000] # Limitamos caracteres para no saturar el LLM
            }

# --- BLOQUE DE PRUEBA INDIVIDUAL ---
if __name__ == "__main__":
    async def test_run():
        navigator = SourceNavigator()
        # Probamos con una URL real (ej: Documentación de Python)
        result = await navigator.fetch_and_clean("https://www.python.org/")
        print(f"Título: {result.get('title')}")
        print(f"Texto (Extracto): {result.get('clean_text')[:200]}...")
    
    asyncio.run(test_run())
