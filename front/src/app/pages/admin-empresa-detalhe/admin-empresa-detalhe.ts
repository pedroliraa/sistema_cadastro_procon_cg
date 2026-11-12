import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';


import { AuthService } from '../../core/auth.service';
import {
  Empresa,
  EmpresaAdminService,
  HistoricoSelo,
  HistoricoStatus,
  NivelSelo,
  ROTULO_STATUS,
  StatusEmpresa,
  formatarData,
  mensagemDeErro,
} from '../../core/empresa-admin.service';
import { formatarCnpj, formatarTelefone } from '../../core/mascaras';
import { imagemDoSelo } from '../../core/selos';

// Mesmas transições do back (empresas/services.py)
const TRANSICOES: Record<StatusEmpresa, StatusEmpresa[]> = {
  ativo: ['suspenso', 'removido'],
  suspenso: ['ativo', 'removido'],
  removido: ['ativo'],
};

@Component({
  selector: 'app-admin-empresa-detalhe',
  imports: [RouterLink, DatePipe],
  templateUrl: './admin-empresa-detalhe.html',
  styleUrl: './admin-empresa-detalhe.css',
})
export class AdminEmpresaDetalhe implements OnInit {
  private readonly service = inject(EmpresaAdminService);
  private readonly route = inject(ActivatedRoute);
  readonly auth = inject(AuthService);

  readonly empresa = signal<Empresa | null>(null);
  readonly historico = signal<HistoricoStatus[]>([]);
  readonly carregando = signal(true);
  readonly salvando = signal(false);
  readonly erro = signal('');
  readonly sucesso = signal('');
  readonly niveisSelo = signal<NivelSelo[]>([]);
  readonly historicoSelo = signal<HistoricoSelo[]>([]);
  readonly formatarCnpj = formatarCnpj;
  readonly formatarTelefone = formatarTelefone;
  readonly imagemDoSelo = imagemDoSelo;

  readonly rotuloStatus = ROTULO_STATUS;
  readonly formatarData = formatarData;

  // Opções do select: só transições válidas e, para analista, sem "removido"
  readonly opcoesStatus = computed<StatusEmpresa[]>(() => {
    const empresa = this.empresa();
    if (!empresa) return [];
    const gestor = this.auth.ehGestor();
    // Sair de "removido" também é só do gestor
    if (empresa.status === 'removido' && !gestor) return [];
    return TRANSICOES[empresa.status].filter((s) => gestor || s !== 'removido');
  });

  private id = 0;

  ngOnInit(): void {
    this.id = Number(this.route.snapshot.paramMap.get('id'));
    this.service.listarNiveisSelo().subscribe({
      next: (niveis) => this.niveisSelo.set(niveis),
    });
    this.carregar();
  }

  carregar(): void {
    this.carregando.set(true);
    this.service.obter(this.id).subscribe({
      next: (empresa) => {
        this.empresa.set(empresa);
        this.carregando.set(false);
      },
      error: () => {
        this.erro.set('Empresa não encontrada.');
        this.carregando.set(false);
      },
    });
    this.carregarHistorico();
  }

  carregarHistorico(): void {
    this.service.historico(this.id).subscribe({
      next: (resposta) => this.historico.set(resposta.results),
    });
  }

    carregarHistoricoSelo(): void {
    this.service.historicoSelo(this.id).subscribe({
      next: (resposta) => this.historicoSelo.set(resposta.results),
    });
  }

  alterarSelo(nivelId: string, campoMotivo: HTMLTextAreaElement): void {
    this.sucesso.set('');

    if (!nivelId) {
      this.erro.set('Escolha o novo selo.');
      return;
    }

    this.salvando.set(true);
    this.erro.set('');

    this.service.alterarSelo(this.id, Number(nivelId), campoMotivo.value.trim()).subscribe({
      next: (empresa) => {
        this.empresa.set(empresa);
        this.salvando.set(false);
        this.sucesso.set(`Selo alterado para "${empresa.selo}".`);
        campoMotivo.value = '';
        this.carregarHistoricoSelo();
      },
      error: (erro) => {
        this.salvando.set(false);
        this.erro.set(mensagemDeErro(erro, 'Não foi possível alterar o selo.'));
      },
    });
  }

  alterarStatus(novoStatus: string, campoMotivo: HTMLTextAreaElement): void {
    const motivo = campoMotivo.value.trim();
    this.sucesso.set('');

    if (!novoStatus) {
      this.erro.set('Escolha o novo status.');
      return;
    }
    if (!motivo) {
      this.erro.set('Informe o motivo da alteração.');
      return;
    }
    if (
      novoStatus === 'removido' &&
      !confirm('Remover esta empresa do programa? Ela deixa de aparecer na consulta pública.')
    ) {
      return;
    }

    this.salvando.set(true);
    this.erro.set('');

    this.service.alterarStatus(this.id, novoStatus as StatusEmpresa, motivo).subscribe({
      next: (empresa) => {
        this.empresa.set(empresa);
        this.salvando.set(false);
        this.sucesso.set(`Status alterado para "${ROTULO_STATUS[empresa.status]}".`);
        campoMotivo.value = '';
        this.carregarHistorico();
        this.carregarHistoricoSelo();
      },
      error: (erro) => {
        this.salvando.set(false);
        this.erro.set(mensagemDeErro(erro, 'Não foi possível alterar o status.'));
      },
    });
  }

  revalidar(campoMotivo: HTMLInputElement): void {
    this.salvando.set(true);
    this.erro.set('');
    this.sucesso.set('');

    this.service.revalidar(this.id, campoMotivo.value.trim()).subscribe({
      next: (empresa) => {
        this.empresa.set(empresa);
        this.salvando.set(false);
        this.sucesso.set(
          `Revalidação registrada. Próxima em ${formatarData(empresa.data_proxima_revalidacao)}.`
        );
        campoMotivo.value = '';
        this.carregarHistorico();
      },
      error: (erro) => {
        this.salvando.set(false);
        this.erro.set(mensagemDeErro(erro, 'Não foi possível registrar a revalidação.'));
      },
    });
  }
}
