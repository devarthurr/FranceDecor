using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using System.Text;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// --- SEU BANCO DE DADOS INTERNO ---
var produtos = new List<Product>
{
    new Product { 
        Id = 1, 
        Name = "TOPOS DE BOLO", 
        Price = 0.00, 
        Description = "Personalizados em camadas e papelaria criativa de luxo.",
        Images = new List<string> { "https://i.ibb.co/pBzF6yVT/Whats-App-Image-1.jpg" } 
    },
    new Product { 
        Id = 2, 
        Name = "PERSONALIZADOS LUXO", 
        Price = 150.00, 
        Description = "Kits premium com detalhes em dourado.",
        Images = new List<string> { "https://i.ibb.co/5WppfRRm/Whats-App-Image-4.jpg" } 
    }
};

// --- ROTAS ---
app.MapGet("/", () => Results.Content(GetIndexHtml(produtos), "text/html", Encoding.UTF8));

app.MapGet("/produto/{id:int}", (int id) => {
    var p = produtos.FirstOrDefault(x => x.Id == id);
    return p != null ? Results.Content(GetProductHtml(p), "text/html", Encoding.UTF8) : Results.NotFound();
});

app.Run();

// --- DEFINIÇÕES E HTML ---

public class Product {
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public double Price { get; set; }
    public List<string> Images { get; set; } = new();
}

partial class Program {
    static string GetIndexHtml(List<Product> lista) {
        var cards = new StringBuilder();
        foreach (var p in lista) {
            cards.Append($"""
            <div class="col">
                <div class="card h-100 shadow-sm border-0" style="border-radius: 20px; overflow: hidden;">
                    <img src="{p.Images[0]}" class="card-img-top" style="height: 250px; object-fit: contain; padding: 15px; background: #fff;">
                    <div class="card-body text-center">
                        <h5 class="fw-bold" style="color: #0047BB;">{p.Name}</h5>
                        <p class="fw-bold" style="color: #D4AF37;">{(p.Price > 0 ? "R$ " + p.Price.ToString("N2") : "Consultar Preço")}</p>
                        <a href="/produto/{p.Id}" class="btn btn-primary w-100 rounded-pill" style="background: #0047BB; border: none;">Ver Detalhes</a>
                    </div>
                </div>
            </div>
            """);
        }
        return $"""
        <!DOCTYPE html><html lang="pt-br"><head><meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>France Decor</title></head><body class="bg-light">
        <nav class="navbar mb-5 shadow" style="background: #0047BB; border-bottom: 4px solid #D4AF37;">
        <div class="container justify-content-center py-2"><span class="navbar-brand fw-bold text-white fs-2">FRANCE DECOR</span></div></nav>
        <div class="container"><div class="row row-cols-1 row-cols-md-3 g-4">{cards}</div></div></body></html>
        """;
    }

    static string GetProductHtml(Product p) {
        return $"""
        <!DOCTYPE html><html lang="pt-br"><head><meta charset="utf-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>{p.Name}</title></head><body class="bg-light">
        <div class="container py-5"><div class="card border-0 shadow-lg rounded-4 p-4">
        <a href="/" class="btn btn-outline-secondary mb-3 rounded-pill" style="width: fit-content;">← Voltar</a>
        <div class="row"><div class="col-md-6 text-center"><img src="{p.Images[0]}" class="img-fluid rounded" style="max-height: 400px;"></div>
        <div class="col-md-6 p-4">
        <h1 class="fw-bold" style="color: #0047BB;">{p.Name}</h1>
        <h2 class="fw-bold mb-4" style="color: #D4AF37;">{(p.Price > 0 ? "R$ " + p.Price.ToString("N2") : "Consultar Valor")}</h2>
        <p class="text-muted fs-5">{p.Description}</p>
        <a href="https://wa.me/5511999999999" class="btn btn-success btn-lg w-100 py-3 fw-bold rounded-pill shadow">ENCOMENDAR NO WHATSAPP</a>
        </div></div></div></div></body></html>
        """;
    }
}