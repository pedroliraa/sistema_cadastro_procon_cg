import { Component, OnInit, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  imports: [],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly carregando = signal(false);
  readonly erro = signal('');

  ngOnInit(): void {
    // Já logado? Vai direto para o painel
    if (this.auth.estaLogado()) {
      this.router.navigate(['/admin/empresas']);
    }
  }

  entrar(usuario: string, senha: string): void {
    if (!usuario.trim() || !senha) {
      this.erro.set('Informe usuário e senha.');
      return;
    }

    this.carregando.set(true);
    this.erro.set('');

    this.auth.login(usuario.trim(), senha).subscribe({
      next: () => {
        this.carregando.set(false);
        this.router.navigate(['/admin/empresas']);
      },
      error: (erro) => {
        this.auth.limparSessao();
        this.carregando.set(false);
        if (erro.status === 400) {
          this.erro.set('Usuário ou senha incorretos.');
        } else if (erro.status === 403) {
          this.erro.set('Este usuário não tem perfil de analista ou gestor.');
        } else {
          this.erro.set('Não foi possível entrar. Verifique se o servidor está rodando.');
        }
      },
    });
  }
}
