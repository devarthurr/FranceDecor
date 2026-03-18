import { neon } from '@neondatabase/serverless';

export default async function Page() {
  // 1. Conecta ao banco usando a variável que a Vercel criou automaticamente
  const sql = neon(process.env.DATABASE_URL);

  // 2. Busca os produtos que você inseriu no SQL Editor
  const produtos = await sql`SELECT * FROM produtos ORDER BY criado_em DESC`;

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Minha Loja de Produtos</h1>
      <hr />
      <div style={{ display: 'grid', gap: '20px' }}>
        {produtos.map((produto) => (
          <div key={produto.id} style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px' }}>
            {/* Exibe o nome e o preço que estão no banco */}
            <h2 style={{ margin: '0 0 10px 0' }}>{produto.nome}</h2>
            <p>{produto.descricao}</p>
            <p><strong>Preço:</strong> R$ {produto.preco}</p>
            <p><strong>Estoque:</strong> {produto.estoque} unidades</p>
            <small>Categoria: {produto.categoria}</small>
          </div>
        ))}
      </div>
    </div>
  );
}