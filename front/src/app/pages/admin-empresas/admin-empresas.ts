import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { AuthService } from '../../core/auth.service';
import {
  Empresa,
  EmpresaAdminService,
  ROTULO_STATUS,
  formatarData,
} from '../../core/empresa-admin.service';

@Component({
  selector: 'app-admin-empresas',
  imports: [RouterLink],
  templateUrl: './admin-empresas.html',
  styleUrl: './admin-empresas.css',
})
export class AdminEmpresas implements OnInit {
  private readonly service = inject(EmpresaAdminService);
  readonly auth = inject(AuthService);

  readonly empresas = signal<Empresa[]>([]);
  readonly total = signal(0);
  readonly pagina = signal(1);
  readonly temProxima = signal(false);
  readonly somenteVencidas = signal(false);
  readonly carregando = signal(false);
  readonly erro = signal('');

  readonly rotuloStatus = ROTULO_STATUS;
  readonly formatarData = formatarData;

  ngOnInit(): void {
    this.carregar();
  }

  carregar(pagina = 1): void {
    this.carregando.set(true);
    this.erro.set('');

    const requisicao = this.somenteVencidas()
      ? this.service.listarRevalidacoesVencidas(pagina)
      : this.service.listar(pagina);

    requisicao.subscribe({
      next: (resposta) => {
        this.empresas.set(resposta.results);
        this.total.set(resposta.count);
        this.temProxima.set(!!resposta.next);
        this.pagina.set(pagina);
        this.carregando.set(false);
      },
      error: () => {
        this.erro.set('Não foi possível carregar as empresas.');
        this.carregando.set(false);
      },
    });
  }

  alternarVencidas(): void {
    this.somenteVencidas.update((valor) => !valor);
    this.carregar(1);
  }
}
