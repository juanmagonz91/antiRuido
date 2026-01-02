import asyncio
import os
import sys
from dotenv import load_dotenv

# Aseguramos que Python encuentre el módulo 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.content_scorer import ContentScorer

# Cargar variables de entorno
load_dotenv()

async def test_gatekeeper():
    # Verificar API Key antes de arrancar
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR CRÍTICO: GOOGLE_API_KEY no encontrada en .env")
        return

    try:
        scorer = ContentScorer()
    except Exception as e:
        print(f"❌ Error inicializando Gemini: {e}")
        return
    
    print("\n--- 🕵️  INICIANDO TEST DEL GATEKEEPER (EDITOR DESPIADADO) ---")
    print(f"Modelo IA: Gemini 1.5 Flash (Vía LangChain)")
    print("-" * 60)

    test_cases = [
        {
            "type": "SEÑAL (Paper Científico)",
            "context_topic": "Machine Learning",
            "context_category": "PROFESIONAL",
            "text": """
            Title: A New Approach to Transformer Efficiency using Sparse Attention
            Abstract: We propose a novel mechanism for sparse attention that reduces computational complexity from O(N^2) to O(N log N).
            This allows for training larger models with significantly less hardware. The method is validated on standard benchmarks like GLUE and SQuAD.
            """
        },
        {
            "type": "RUIDO (Chisme)",
            "context_topic": "Noticias Generales",
            "context_category": "PROFESIONAL", # Probamos si filtra ruido incluso si pedimos algo serio
            "text": """
            ¡INCREÍBLE! ¡No creerás con quién está saliendo esta celebridad ahora!
            Las fotos exclusivas revelan que X y Y fueron vistos cenando juntos. 
            ¡El drama explota en redes sociales! Mira las reacciones de sus ex-parejas.
            Haz clic aquí para ver la galería completa de fotos borrosas.
            """
        },
        {
            "type": "DUDOSO (Clickbait de Ventas)",
            "context_topic": "Tecnología",
            "context_category": "PROFESIONAL",
            "text": """
            Top 10 Gadgets que necesitas comprar este 2024.
            El número 7 te sorprenderá. Estos dispositivos cambiarán tu vida para siempre.
            Incluye enlaces de afiliados a Amazon para cada producto.
            Resumen: Un reloj inteligente, una freidora de aire y unos auriculares.
            """
        }
    ]

    for case in test_cases:
        print(f"\n🧪 Probando caso: {case['type']}")
        print(f"   Contexto: {case['context_topic']} ({case['context_category']})")
        
        # LLAMADA AL SERVICIO (Con los argumentos correctos)
        result = await scorer.analyze_content(
            content=case['text'], 
            topic=case['context_topic'],
            category=case['context_category']
        )
        
        # Mapeo de resultados
        score = result.get('quality_score', 0.0)
        decision = result.get('decision', 'BLOCK')
        reason = result.get('analysis_reasoning', 'Sin razón')
        is_bait = result.get('is_clickbait', False)
        
        # Formato de consola con colores
        color = "\033[92m" if decision == "SHOW" else "\033[91m" # Verde/Rojo
        reset = "\033[0m"
        
        print(f"   Score IA: {score}")
        print(f"   Clickbait: {is_bait}")
        print(f"   Veredicto: {color}{decision}{reset}")
        print(f"   Razón: {reason}")
        
        # Validación de lógica del test
        if "SEÑAL" in case["type"] and decision == "BLOCK":
            print("   ⚠️  FAIL: FALSO NEGATIVO DETECTADO")
        elif "RUIDO" in case["type"] and decision == "SHOW":
            print("   ⚠️  FAIL: FALSO POSITIVO DETECTADO")
        else:
            print("   ✅ PASS: Comportamiento esperado")

if __name__ == "__main__":
    asyncio.run(test_gatekeeper())
