import { Component, inject, signal, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { API_URL } from '../../core/api';
import { imagemDoSelo } from '../../core/selos'

interface EmpresaDestaque {
  id: number;
  razao_social: string;
  foto: string | null;
  selo: string | null;
  areas: { id: number; nome: string }[];
}

interface RespostaEmpresas {
  count: number;
  results: EmpresaDestaque[];
}

@Component({
  selector: 'app-inicio',
  imports: [],
  templateUrl: './inicio.html',
  styleUrl: './inicio.css',
})
export class Inicio implements OnInit {
  private readonly router = inject(Router);
  private readonly http = inject(HttpClient);

  readonly empresasDestaque = signal<EmpresaDestaque[]>([]);
  readonly imagemDoSelo = imagemDoSelo

  ngOnInit(): void {
    this.http
      .get<RespostaEmpresas>(`${API_URL}/publico/empresas/`)
      .subscribe({
        next: (resposta) => {
          this.empresasDestaque.set(resposta.results.slice(0, 4));
        },
        error: (erro) => {
          console.error('Erro ao carregar empresas em destaque:', erro);
        },
      });
  }

  pesquisar(event: Event): void {
  event.preventDefault();

  const formulario = event.target as HTMLFormElement;
  const dados = new FormData(formulario);
  const nome = String(dados.get('empresa') ?? '').trim();

  if (!nome) {
    return;
  }

  this.router.navigate(['/consulta-publica'], {
    queryParams: { nome },
  });
}
}
