using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;

var builder = WebApplication.CreateBuilder(args);

// Configuração de Autenticação (Login)
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options => { options.LoginPath = "/Login"; });
builder.Services.AddAuthorization();
builder.Services.AddControllersWithViews();

var app = builder.Build();

// BANCO DE DADOS EM MEMÓRIA (Lista de Produtos)
// Para não sumir, você preenche essa lista aqui no código
var produtos = new List<Produto>
{
    new Produto { 
        Id = 1, 
        Nome = "TOPOS DE BOLO", 
        Preco = 0.0, 
        Descricao = "Modelos variados", 
        Imagens = new List<string> { 
            "https://i.ibb.co/pBzF6yVT/Whats-App-Image-1.jpg",
            "https://i.ibb.co/YBK2101k/Whats-App-Image-2.jpg" 
        } 
    }
};

app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();

// --- ROTAS ---

// Vitrine Principal
app.MapGet("/", () => Results.Extensions.RazorView("/Views/Index.cshtml", produtos));

// Detalhes do Produto
app.MapGet("/produto/{id:int}", (int id) => {
    var p = produtos.FirstOrDefault(x => x.Id == id);
    return p is not null ? Results.Extensions.RazorView("/Views/Produto.cshtml", p) : Results.NotFound();
});

// Admin (Protegido)
app.MapGet("/admin", [Authorize] () => Results.Extensions.RazorView("/Views/Admin.cshtml", produtos));

// Login
app.MapGet("/login", () => Results.Extensions.RazorView("/Views/Login.cshtml"));
app.MapPost("/login", async (HttpContext context, string username, string password) => {
    if (username == "admin" && password == "password123") {
        var claims = new List<Claim> { new Claim(ClaimTypes.Name, username) };
        var claimsIdentity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
        await context.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, new ClaimsPrincipal(claimsIdentity));
        return Results.Redirect("/admin");
    }
    return Results.Redirect("/login?error=1");
});

app.MapGet("/logout", async (HttpContext context) => {
    await context.SignOutAsync();
    return Results.Redirect("/");
});

app.Run();

// CLASSES DE MODELO
public class Produto {
    public int Id { get; set; }
    public string Nome { get; set; }
    public string Descricao { get; set; }
    public double Preco { get; set; }
    public List<string> Imagens { get; set; }
}