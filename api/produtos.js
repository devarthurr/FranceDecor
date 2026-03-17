import fs from "fs";

const filePath = "./data.json";

export default async function handler(req, res) {

  if (req.method === "GET") {
    const data = fs.readFileSync(filePath);
    return res.status(200).json(JSON.parse(data));
  }

  if (req.method === "POST") {
    const produtos = JSON.parse(fs.readFileSync(filePath));
    const novo = req.body;
    novo.id = Date.now();
    produtos.push(novo);
    fs.writeFileSync(filePath, JSON.stringify(produtos, null, 2));
    return res.status(200).json({ message: "Criado" });
  }

  if (req.method === "PUT") {
    let produtos = JSON.parse(fs.readFileSync(filePath));
    const atualizado = req.body;
    produtos = produtos.map(p => p.id === atualizado.id ? atualizado : p);
    fs.writeFileSync(filePath, JSON.stringify(produtos, null, 2));
    return res.status(200).json({ message: "Atualizado" });
  }

  if (req.method === "DELETE") {
    let produtos = JSON.parse(fs.readFileSync(filePath));
    const { id } = req.body;
    produtos = produtos.filter(p => p.id !== id);
    fs.writeFileSync(filePath, JSON.stringify(produtos, null, 2));
    return res.status(200).json({ message: "Deletado" });
  }
}