import { Component, inject, signal, OnInit } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import {
  AreaAtuacao,
  EmpresaAdminService,
  NivelSelo,
  mensagemDeErro,
} from '../../core/empresa-admin.service';
import {
  formatarCnpj, formatarTelefone, limparCnpj, limparTelefone,
} from '../../core/mascaras';
import { finalize } from 'rxjs';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-admin-empresa-formulario',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './admin-empresa-formulario.html',
  styleUrl: './admin-empresa-formulario.css',
})
export class AdminEmpresaFormulario implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly empresaService = inject(EmpresaAdminService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  readonly empresaId = Number(this.route.snapshot.paramMap.get('id')) || null;
  readonly fotoSelecionada = signal<File | null>(null);
  readonly fotoPreview = signal<string | null>(null);
  readonly niveisSelo = signal<NivelSelo[]>([]);

  selecionarFoto(event: Event): void {
    const input = event.target as HTMLInputElement;
    const arquivo = input.files?.[0];

    if (!arquivo) return;

    const tiposPermitidos = ['image/jpeg', 'image/png', 'image/webp'];

    if (!tiposPermitidos.includes(arquivo.type)) {
      this.fotoSelecionada.set(null);
      this.mensagemErro.set('Selecione uma imagem JPG, PNG ou WebP.');
      input.value = '';
      return;
    }

    this.fotoSelecionada.set(arquivo);
    this.mensagemErro.set('');

    const leitor = new FileReader();

    leitor.onload = () => {
      this.fotoPreview.set(leitor.result as string);
    };

    leitor.readAsDataURL(arquivo);
  }

  selecionarAreas(event: Event): void {
    const select = event.target as HTMLSelectElement;

    const areasSelecionadas = Array.from(select.selectedOptions).map(
      (option) => Number(option.value)
    );

    this.formulario.controls.areas.setValue(areasSelecionadas);
  }

  invalido(campo: string): boolean {
    const controle = this.formulario.get(campo);
    return !!controle && controle.invalid && (controle.touched || controle.dirty);
  }

  mascararCnpj(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.formulario.controls.cnpj.setValue(formatarCnpj(input.value));
  }

  mascararTelefone(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.formulario.controls.telefone.setValue(formatarTelefone(input.value));
  }

  salvarEmpresa(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }



    const valores = this.formulario.getRawValue();
    const dados = new FormData();

    dados.append('razao_social', valores.razao_social);
    dados.append('cnpj', limparCnpj(valores.cnpj));
    dados.append('endereco', valores.endereco);
    dados.append('bairro', valores.bairro);
    dados.append('cidade', valores.cidade);
    dados.append('telefone', limparTelefone(valores.telefone));
    dados.append('email', valores.email);

    valores.areas.forEach((areaId) => {
      dados.append('areas', String(areaId));
    });

    if (valores.nivel_selo !== null) {
      dados.append('nivel_selo', String(valores.nivel_selo));
    }

    const foto = this.fotoSelecionada();

    if (foto) {
      dados.append('foto', foto);
    }
    this.mensagemSucesso.set('');
    this.mensagemErro.set('');

    this.salvando.set(true);

    const requisicao = this.empresaId !== null
      ? this.empresaService.editar(this.empresaId, dados)
      : this.empresaService.cadastrar(dados);

    requisicao
      .pipe(finalize(() => this.salvando.set(false)))
      .subscribe({
        next: (empresa) => {
          const acao = this.empresaId !== null ? 'atualizada' : 'cadastrada';

          this.router.navigate(['/admin/empresas', empresa.id], {
            state: { sucesso: `Empresa "${empresa.razao_social}" ${acao} com sucesso!` },
          });
        },
        error: (erro) => {
          console.error('Erro ao cadastrar empresa:', erro);
          const acao = this.empresaId !== null ? 'atualizar' : 'cadastrar';

          this.mensagemErro.set(
            mensagemDeErro(
              erro,
              `Não foi possível ${acao} a empresa. Verifique os dados e tente novamente.`
            )
          );
        },
      });
  }

  readonly areasDisponiveis = signal<AreaAtuacao[]>([]);
  readonly mensagemSucesso = signal('');
  readonly mensagemErro = signal('');
  readonly salvando = signal(false);

  ngOnInit(): void {
    this.empresaService.listarAreas().subscribe({
      next: (areas) => {
        this.areasDisponiveis.set(areas);
      },
      error: () => {
        console.error('Não foi possível carregar as áreas de atuação.');
      },

    });

    this.empresaService.listarNiveisSelo().subscribe({
      next: (niveis) => this.niveisSelo.set(niveis),
      error: () => console.error('Não foi possível carregar os selos.'),
    });

    if (this.empresaId !== null) {
      this.empresaService.obter(this.empresaId).subscribe({
        next: (empresa) => {
          this.formulario.patchValue({
            razao_social: empresa.razao_social,
            cnpj: formatarCnpj(empresa.cnpj),
            endereco: empresa.endereco,
            bairro: empresa.bairro,
            cidade: empresa.cidade,
            telefone: formatarTelefone(empresa.telefone),
            email: empresa.email,
            areas: empresa.areas,
            nivel_selo: empresa.nivel_selo_atual,
          });
          if (empresa.foto) {
            this.fotoPreview.set(empresa.foto);
          }
        },
        error: () => {
          this.mensagemErro.set(
            'Não foi possível carregar os dados da empresa.'
          );
        },
      });
    }
  }


  readonly formulario = this.fb.nonNullable.group({
    razao_social: ['', Validators.required],
    cnpj: [
      '',
      [
        Validators.required,
        Validators.pattern(/^[0-9A-Z]{2}\.[0-9A-Z]{3}\.[0-9A-Z]{3}\/[0-9A-Z]{4}-\d{2}$/),
      ],
    ],
    endereco: ['', Validators.required],
    bairro: ['', Validators.required],
    cidade: ['', Validators.required],
    telefone: [
      '',
      [Validators.required, Validators.pattern(/^\(\d{2}\) \d{4,5}-\d{4}$/)],
    ],
    email: ['', [Validators.required, Validators.email]],
    areas: this.fb.nonNullable.control<number[]>([], Validators.required),
    nivel_selo: this.fb.control<number | null>(null),
  });
}

