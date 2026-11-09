import { Injectable, PLATFORM_ID, computed, inject, signal } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, switchMap, tap } from 'rxjs';

import { API_URL } from './api';

export interface Usuario {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  perfil: 'Analista' | 'Gestor' | null;
}

const CHAVE_TOKEN = 'procon_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly noNavegador = isPlatformBrowser(inject(PLATFORM_ID));

  readonly usuario = signal<Usuario | null>(null);
  readonly ehGestor = computed(() => this.usuario()?.perfil === 'Gestor');

  // localStorage só existe no navegador (no SSR não existe)
  get token(): string | null {
    return this.noNavegador ? localStorage.getItem(CHAVE_TOKEN) : null;
  }

  estaLogado(): boolean {
    return !!this.token;
  }

  login(username: string, password: string): Observable<Usuario> {
    return this.http
      .post<{ token: string }>(`${API_URL}/auth/login/`, { username, password })
      .pipe(
        tap((resposta) => localStorage.setItem(CHAVE_TOKEN, resposta.token)),
        switchMap(() => this.carregarUsuario())
      );
  }

  // GET /api/auth/me/ → dados e perfil do usuário logado
  carregarUsuario(): Observable<Usuario> {
    return this.http
      .get<Usuario>(`${API_URL}/auth/me/`)
      .pipe(tap((usuario) => this.usuario.set(usuario)));
  }

  limparSessao(): void {
    if (this.noNavegador) {
      localStorage.removeItem(CHAVE_TOKEN);
    }
    this.usuario.set(null);
  }

  logout(): void {
    this.limparSessao();
    this.router.navigate(['/login']);
  }
}
