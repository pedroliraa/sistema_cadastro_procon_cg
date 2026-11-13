import { Component, inject, signal, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';

import { API_URL } from '../../core/api';
import { NOMES_SELOS, imagemDoSelo } from '../../core/selos';

interface EmpresaPublica {
  id: number;
  razao_social: string;
  foto: string | null;
  endereco: string;
  bairro: string;
  cidade: string;
  areas: { id: number; nome: string }[];
  selo: string | null;
}

interface RespostaEmpresas {
  count: number;
  results: EmpresaPublica[];
}

@Component({
  selector: 'app-consulta-publica',
  imports: [],
  templateUrl: './consulta-publica.html',
  styleUrl: './consulta-publica.css',
})
export class ConsultaPublica implements OnInit {
  private readonly http = inject(HttpClient);
  readonly route = inject(ActivatedRoute);

  readonly empresas = signal<EmpresaPublica[]>([]);
  readonly carregando = signal(false);
  readonly erro = signal('');
  readonly pesquisaRealizada = signal(false);
  readonly areaSelecionada = signal('');
  readonly seloSelecionado = signal('');
  readonly menuSeloAberto = signal(false);

  readonly nomesSelos = NOMES_SELOS;
  readonly imagemDoSelo = imagemDoSelo;

  private nomeAtual = '';

  ngOnInit(): void {
    const params = this.route.snapshot.queryParamMap;
    this.nomeAtual = (params.get('nome') ?? '').trim();
    this.seloSelecionado.set(params.get('selo') ?? '');
    this.consultar();
  }

  private consultar(): void {
    const params: Record<string, string> = {};
    if (this.nomeAtual) params['nome'] = this.nomeAtual;
    if (this.areaSelecionada()) params['area'] = this.areaSelecionada();
    if (this.seloSelecionado()) params['selo'] = this.seloSelecionado();

    this.carregando.set(true);
    this.erro.set('');

    this.http
      .get<RespostaEmpresas>(`${API_URL}/publico/empresas/`, { params })
      .subscribe({
        next: (resposta) => {
          this.empresas.set(resposta.results);
          this.pesquisaRealizada.set(true);
          this.carregando.set(false);
        },
        error: () => {
          this.erro.set('Não foi possível realizar a consulta.');
          this.carregando.set(false);
        },
      });
  }

  buscar(nome: string): void {
    this.nomeAtual = nome.trim();
    this.consultar();
  }

  buscarPorArea(area: string): void {
    this.areaSelecionada.set(area);
    this.consultar();
  }

  alternarMenuSelo(): void {
    this.menuSeloAberto.update((aberto) => !aberto);
  }

  filtrarPorSelo(selo: string): void {
    this.seloSelecionado.set(selo);
    this.menuSeloAberto.set(false);
    this.consultar();
  }

  // "Todas": remove todos os filtros e lista tudo
  limparFiltros(): void {
    this.nomeAtual = '';
    this.areaSelecionada.set('');
    this.seloSelecionado.set('');
    this.menuSeloAberto.set(false);
    this.consultar();
  }
}
