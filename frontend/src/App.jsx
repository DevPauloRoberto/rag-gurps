import { useState } from "react";

function formatarInline(texto) {
  if (!texto) return null;
  const partes = texto.split(/(\*\*.*?\*\*|`.*?`|\*[^*]+?\*)/g);
  return partes.map((parte, i) => {
    if (parte.startsWith("**") && parte.endsWith("**")) {
      return (
        <strong key={i} className="font-bold text-amber-300">
          {parte.slice(2, -2)}
        </strong>
      );
    }
    if (parte.startsWith("`") && parte.endsWith("`")) {
      return (
        <code
          key={i}
          className="bg-zinc-800 text-amber-300 px-1.5 py-0.5 rounded text-xs font-mono"
        >
          {parte.slice(1, -1)}
        </code>
      );
    }
    if (parte.startsWith("*") && parte.endsWith("*") && parte.length > 2) {
      return (
        <em key={i} className="italic text-zinc-300">
          {parte.slice(1, -1)}
        </em>
      );
    }
    return parte;
  });
}

function RenderMarkdown({ texto }) {
  if (!texto) return null;
  const linhas = texto.split("\n");
  const elementos = [];
  let i = 0;

  while (i < linhas.length) {
    const linha = linhas[i];
    const trim = linha.trim();

    // Ignora linhas vazias
    if (!trim) {
      i++;
      continue;
    }

    // Linha divisória ---
    if (/^-{3,}$/.test(trim)) {
      elementos.push(<hr key={i} className="border-zinc-800 my-3" />);
      i++;
      continue;
    }

    // Tabelas Markdown | col1 | col2 |
    if (trim.startsWith("|") && trim.endsWith("|")) {
      const linhasTabela = [];
      while (i < linhas.length && linhas[i].trim().startsWith("|")) {
        linhasTabela.push(linhas[i].trim());
        i++;
      }
      const linhasValidas = linhasTabela.filter(
        (l) => !/^\|[\s\-:|]+\|$/.test(l)
      );
      if (linhasValidas.length > 0) {
        const cabecalho = linhasValidas[0]
          .slice(1, -1)
          .split("|")
          .map((c) => c.trim());
        const corpo = linhasValidas.slice(1).map((l) =>
          l
            .slice(1, -1)
            .split("|")
            .map((c) => c.trim())
        );
        elementos.push(
          <div key={`table-${i}`} className="overflow-x-auto my-3">
            <table className="w-full text-xs text-left border border-zinc-800 rounded-lg overflow-hidden">
              <thead className="bg-zinc-950 text-amber-400 border-b border-zinc-800">
                <tr>
                  {cabecalho.map((col, idx) => (
                    <th key={idx} className="px-3 py-2 font-semibold">
                      {formatarInline(col)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800">
                {corpo.map((row, rIdx) => (
                  <tr key={rIdx} className="hover:bg-zinc-800/40">
                    {row.map((cel, cIdx) => (
                      <td key={cIdx} className="px-3 py-2 text-zinc-200">
                        {formatarInline(cel)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      continue;
    }

    // Títulos #, ##, ###, ####
    if (trim.startsWith("#### ")) {
      elementos.push(
        <h4 key={i} className="text-sm font-bold text-amber-400 mt-3 mb-1">
          {formatarInline(trim.slice(5))}
        </h4>
      );
      i++;
      continue;
    }
    if (trim.startsWith("### ")) {
      elementos.push(
        <h3 key={i} className="text-base font-bold text-amber-400 mt-4 mb-1">
          {formatarInline(trim.slice(4))}
        </h3>
      );
      i++;
      continue;
    }
    if (trim.startsWith("## ")) {
      elementos.push(
        <h2 className="text-lg font-bold text-amber-400 mt-4 mb-2 border-b border-zinc-800 pb-1" key={i}>
          {formatarInline(trim.slice(3))}
        </h2>
      );
      i++;
      continue;
    }
    if (trim.startsWith("# ")) {
      elementos.push(
        <h1 key={i} className="text-xl font-bold text-amber-400 mt-4 mb-2">
          {formatarInline(trim.slice(2))}
        </h1>
      );
      i++;
      continue;
    }

    // Listas com - ou *
    if (trim.startsWith("- ") || trim.startsWith("* ")) {
      const itens = [];
      while (
        i < linhas.length &&
        (linhas[i].trim().startsWith("- ") || linhas[i].trim().startsWith("* "))
      ) {
        itens.push(linhas[i].trim().slice(2));
        i++;
      }
      elementos.push(
        <ul key={`ul-${i}`} className="list-disc list-inside space-y-1 my-2 text-zinc-200">
          {itens.map((item, idx) => (
            <li key={idx} className="leading-relaxed">
              {formatarInline(item)}
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // Listas numeradas 1. 2.
    if (/^\d+\.\s/.test(trim)) {
      const itens = [];
      while (i < linhas.length && /^\d+\.\s/.test(linhas[i].trim())) {
        itens.push(linhas[i].trim().replace(/^\d+\.\s/, ""));
        i++;
      }
      elementos.push(
        <ol key={`ol-${i}`} className="list-decimal list-inside space-y-1 my-2 text-zinc-200">
          {itens.map((item, idx) => (
            <li key={idx} className="leading-relaxed">
              {formatarInline(item)}
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // Parágrafo comum
    elementos.push(
      <p key={i} className="leading-relaxed my-1.5 text-zinc-100">
        {formatarInline(linha)}
      </p>
    );
    i++;
  }

  return <div className="space-y-1 text-sm">{elementos}</div>;
}

export default function App() {
  const [mensagens, setMensagens] = useState([]);
  const [pergunta, setPergunta] = useState("");
  const [usarHyde, setUsarHyde] = useState(false);
  const [carregando, setCarregando] = useState(false);

  async function enviarPergunta(e) {
    e.preventDefault();
    if (!pergunta.trim() || carregando) return;

    const textoUsuario = pergunta;
    const historicoRecente = mensagens.slice(-4).map((m) => ({
      autor: m.autor,
      texto: m.texto,
    }));

    setPergunta("");
    setMensagens((atual) => [...atual, { autor: "usuario", texto: textoUsuario }]);
    setCarregando(true);

    try {
      const res = await fetch("http://localhost:8000/rag/perguntar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pergunta: textoUsuario,
          k: 5,
          usar_hyde: usarHyde,
          historico: historicoRecente,
        }),
      });
      const dados = await res.json();

      setMensagens((atual) => [
        ...atual,
        {
          autor: "ia",
          texto: dados.resposta,
          textoBusca: dados.texto_busca_usado,
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
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-bold text-amber-400">🎲 Mestre GURPS RAG</h1>
          {mensagens.length > 0 && (
            <button
              onClick={() => setMensagens([])}
              className="text-xs text-zinc-400 hover:text-zinc-200 border border-zinc-700 px-2.5 py-1 rounded-lg cursor-pointer"
            >
              Nova Conversa
            </button>
          )}
        </div>
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
            Peça ajuda para criar uma ficha, escolher armas iniciais, calcular pontos ou tirar dúvidas de regras...
          </p>
        )}

        {mensagens.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.autor === "usuario" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-3xl rounded-2xl px-5 py-4 ${
                msg.autor === "usuario"
                  ? "bg-amber-600 text-white"
                  : "bg-zinc-900 border border-zinc-800 text-zinc-100 w-full"
              }`}
            >
              {msg.autor === "usuario" ? (
                <p className="whitespace-pre-wrap leading-relaxed">{msg.texto}</p>
              ) : (
                <RenderMarkdown texto={msg.texto} />
              )}

              {msg.fontes?.length > 0 && (
                <details className="mt-4 text-xs text-zinc-400 border-t border-zinc-800 pt-2">
                  <summary className="cursor-pointer hover:text-amber-400">
                    Ver {msg.fontes.length} trechos consultados (busca: "{msg.textoBusca}")
                  </summary>
                  <div className="mt-2 space-y-2">
                    {msg.fontes.map((f, idx) => (
                      <div key={idx} className="p-2 bg-zinc-950 rounded border border-zinc-800">
                        <span className="font-semibold text-amber-400">
                          {f.fonte} {f.pagina !== null ? `(pág. ${f.pagina})` : ""}
                        </span>
                        <p className="mt-1 text-zinc-400 whitespace-pre-wrap">{f.trecho}</p>
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
            Consultando livros e tabelas de GURPS...
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
            placeholder="Ex: Monte uma ficha completa de 150 pontos de um atirador furtivo moderno (NT8) com pistola e rifle"
            className="flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-amber-500"
          />
          <button
            type="submit"
            disabled={carregando}
            className="bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-zinc-950 font-semibold px-6 py-3 rounded-xl text-sm transition cursor-pointer"
          >
            Enviar
          </button>
        </div>
      </form>
    </div>
  );
}
