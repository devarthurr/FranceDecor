using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllersWithViews();

var app = builder.Build();

// --- SEU BANCO DE DADOS INTERNO ---
var produtos = new List<Product>
{
    new Product { 
        Id = 1, 
        Name = "TOPOS DE BOLO", 
        Price = 0.00, 
        Description = "Modelos personalizados para festas.",
        ImageUrls = new List<string> {
            "https://i.ibb.co/pBzF6yVT/Whats-App-Image-1.jpg",
            "https://i.ibb.co/YBK2101k/Whats-App-Image-2.jpg",
            "https://i.ibb.co/gL4t1F4P/Whats-App-Image-3.jpg"
        }
    },
    new Product { 
        Id = 2, 
        Name = "PERSONALIZADOS LUXO", 
        Price = 150.00, 
        Description = "Kits de luxo completos.",
        ImageUrls = new List<string> { "https://i.ibb.co/5WppfRRm/Whats-App-Image-4.jpg" }
    }
};

app.UseStaticFiles();
app.UseRouting();

// Rota: Vitrine Principal
app.MapGet("/", () => Results.Extensions.RazorView("/Views/Index.cshtml", produtos));

// Rota: Detalhes do Produto
app.MapGet("/produto/{id:int}", (int id) => {
    var p = produtos.FirstOrDefault(x => x.Id == id);
    return p != null ? Results.Extensions.RazorView("/Views/Produto.cshtml", p) : Results.NotFound();
});

app.Run();

// Modelo do Produto
public class Product {
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public double Price { get; set; }
    public List<string> ImageUrls { get; set; } = new();
}

// Extensão necessária para rodar Razor sem Controllers complexos
public static class RazorResultsExtensions {
    public static IResult RazorView(this IResultExtensions extensions, string viewPath, object model) {
        return new RazorViewResult(viewPath, model);
    }
}

public class RazorViewResult : IResult {
    private readonly string _viewPath;
    private readonly object _model;
    public RazorViewResult(string viewPath, object model) { _viewPath = viewPath; _model = model; }
    public async Task ExecuteAsync(HttpContext httpContext) {
        var factory = httpContext.RequestServices.GetRequiredService<Microsoft.AspNetCore.Mvc.Razor.IRazorViewEngine>();
        // Lógica simplificada para exemplo; em produção usa-se Controller/View padrão
    }
}