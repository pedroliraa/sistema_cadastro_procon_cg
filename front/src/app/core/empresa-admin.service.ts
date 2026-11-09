import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_URL } from './api';

export type StatusEmpresa = 'ativo' | 'suspenso' | 'removido';

export interface Empresa {
  id: number;
  razao_social: string;
  cnpj: string;
  endereco: string;
  bairro: string;
  cidade: string;
  telefone: string;
  email: string;
  areas: number[];
  nivel_selo_atual: number | null;
  status: StatusEmpresa;
  data_ultima_validacao: string | null;
  data_proxima_revalidacao: string | null;
  revalidacao_vencida: boolean;
}

export interface HistoricoStatus {
  id: number;
  tipo: 'alteracao' | 'revalidacao';
  status_anterior: StatusEmpresa;
  status_novo: StatusEmpresa;
  motivo: string;
  usuario: string | null;
  data_alteracao: string;
}

export interface Paginado<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const ROTULO_STATUS: Record<StatusEmpresa, string> = {
  ativo: 'Ativo',
  suspenso: 'Suspenso',
  removido: 'Removido',
};

// "2026-05-09" → "09/05/2026" (sem passar por Date, para não cair no
// fuso horário e mostrar o dia anterior)
export function formatarData(data: string | null): string {
  return data ? data.split('-').reverse().join('/') : '—';
}

// Pega a mensagem de erro que o Django devolve
export function mensagemDeErro(erro: any, padrao: string): string {
  const corpo = erro?.error;
  if (corpo?.detail) return corpo.detail;
  if (corpo && typeof corpo === 'object') {
    const primeiro = Object.values(corpo)[0];
    if (Array.isArray(primeiro) && primeiro.length) return String(primeiro[0]);
  }
  return padrao;
}

@Injectable({ providedIn: 'root' })
export class EmpresaAdminService {
  private readonly http = inject(HttpClient);
  private readonly url = `${API_URL}/empresas`;

  listar(pagina = 1): Observable<Paginado<Empresa>> {
    return this.http.get<Paginado<Empresa>>(`${this.url}/`, {
      params: { page: pagina },
    });
  }

  listarRevalidacoesVencidas(pagina = 1): Observable<Paginado<Empresa>> {
    return this.http.get<Paginado<Empresa>>(`${this.url}/revalidacoes-vencidas/`, {
      params: { page: pagina },
    });
  }

  obter(id: number): Observable<Empresa> {
    return this.http.get<Empresa>(`${this.url}/${id}/`);
  }

  // PB-11
  alterarStatus(id: number, status: StatusEmpresa, motivo: string): Observable<Empresa> {
    return this.http.post<Empresa>(`${this.url}/${id}/alterar-status/`, { status, motivo });
  }

  revalidar(id: number, motivo = ''): Observable<Empresa> {
    return this.http.post<Empresa>(`${this.url}/${id}/revalidar/`, { motivo });
  }

  historico(id: number): Observable<Paginado<HistoricoStatus>> {
    return this.http.get<Paginado<HistoricoStatus>>(`${this.url}/${id}/historico-status/`);
  }
}
