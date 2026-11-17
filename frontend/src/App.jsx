import { useState } from "react";

export default function App() {
  const [mensagens, setMensagens] = useState([]);
  const [pergunta, setPergunta] = useState("");
  const [usarHyde, setUsarHyde] = useState(false);
  const [carregando, setCarregando] = useState(false);

  async function enviarPergunta(e) {
    e.preventDefault();
    if (!pergunta.trim() || carregando) return;

    const textoUsuario = pergunta;
    setPergunta("");
    setMensagens((atual) => [...atual, { autor: "usuario", texto: textoUsuario }]);
    setCarregando(true);

    try {
      const res = await fetch("http://localhost:8000/rag/perguntar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pergunta: textoUsuario,
          k: 4,
          usar_hyde: usarHyde,
        }),
      });
      const dados = await res.json();

      setMensagens((atual) => [
        ...atual,
        {
          autor: "ia",
          texto: dados.resposta,
          fontes: dados.chunks_recuperados || [],
        },
      ]);
    } catch {
      setMensagens((atual) => [
        ...atual,
        { autor: "ia", texto: "Erro ao conectar com a API do GURPS RAG." },
      ]);
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="flex flex-col h-screen bg-zinc-950 text-zinc-100">
      {/* Topo */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-900">
        <h1 className="text-lg font-bold text-amber-400">🎲 Mestre GURPS RAG</h1>
        <label className="flex items-center gap-2 text-sm text-zinc-300 cursor-pointer">
          <input
            type="checkbox"
            checked={usarHyde}
            onChange={(e) => setUsarHyde(e.target.checked)}
            className="accent-amber-500 w-4 h-4"
          />
          Usar HyDE
        </label>
      </header>

      {/* Área de Mensagens */}
      <main className="flex-1 overflow-y-auto p-6 space-y-4 max-w-4xl w-full mx-auto">
        {mensagens.length === 0 && (
          <p className="text-center text-zinc-500 mt-20">
            Faça uma pergunta sobre as regras de GURPS indexadas no banco...
          </p>
        )}

        {mensagens.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.autor === "usuario" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-2xl rounded-2xl px-4 py-3 ${
                msg.autor === "usuario"
                  ? "bg-amber-600 text-white"
                  : "bg-zinc-900 border border-zinc-800 text-zinc-100"
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{msg.texto}</p>

              {msg.fontes?.length > 0 && (
                <details className="mt-3 text-xs text-zinc-400 border-t border-zinc-800 pt-2">
                  <summary className="cursor-pointer hover:text-amber-400">
                    Ver {msg.fontes.length} trechos consultados
                  </summary>
                  <div className="mt-2 space-y-2">
                    {msg.fontes.map((f, idx) => (
                      <div key={idx} className="p-2 bg-zinc-950 rounded border border-zinc-800">
                        <span className="font-semibold text-amber-400">
                          {f.fonte} {f.pagina !== null ? `(pág. ${f.pagina})` : ""}
                        </span>
                        <p className="mt-1 text-zinc-400 line-clamp-3">{f.trecho}</p>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          </div>
        ))}

        {carregando && (
          <div className="text-sm text-zinc-400 animate-pulse">
            Consultando livros de GURPS...
          </div>
        )}
      </main>

      {/* Input */}
      <form
        onSubmit={enviarPergunta}
        className="p-4 border-t border-zinc-800 bg-zinc-900"
      >
        <div className="max-w-4xl mx-auto flex gap-3">
          <input
            type="text"
            value={pergunta}
            onChange={(e) => setPergunta(e.target.value)}
            placeholder="Ex: Como funciona o teste de Esquiva e Aparar?"
            className="flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-amber-500"
          />
          <button
            type="submit"
            disabled={carregando}
            className="bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-zinc-950 font-semibold px-6 py-3 rounded-xl text-sm transition"
          >
            Enviar
          </button>
        </div>
      </form>
    </div>
  );
}
