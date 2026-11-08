import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface EmpresaPublica {
  id: number;
  razao_social: string;
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
export class ConsultaPublica {
  private readonly http = inject(HttpClient);

  readonly empresas = signal<EmpresaPublica[]>([]);
  readonly carregando = signal(false);
  readonly erro = signal('');
  readonly pesquisaRealizada = signal(false);

  buscar(nome: string): void {
    const termo = nome.trim();

    if (!termo) {
      this.empresas.set([]);
      this.erro.set('');
      this.pesquisaRealizada.set(false);
      return;
    }

    this.carregando.set(true);
    this.erro.set('');

    this.http.get<RespostaEmpresas>(
      'http://127.0.0.1:8000/api/publico/empresas/',
      { params: { nome: termo } }
    ).subscribe({
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
}