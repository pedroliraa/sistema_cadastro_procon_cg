import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-inicio',
  imports: [],
  templateUrl: './inicio.html',
  styleUrl: './inicio.css',
})
export class Inicio {
  private readonly router = inject(Router);

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