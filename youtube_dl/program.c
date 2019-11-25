#include <stdio.h>

int beker();
int szorzotabla();
int maxatlag(int db);
int faktor(int szam);

int main()
{
  int a, ujra;
  do
  {
    a = szorzotabla();
    a = maxatlag(a);
    a = faktor(a);
    printf("Ujra? (1/0)");
    scanf("%d", &ujra);
  } while (ujra);
}

int szorzotabla()
{
  int sor, oszlop, i, j, limit = 5, max = 4;
  sor = beker();
  oszlop = beker();
  if (sor > limit || oszlop > limit)
  {
    sor = max;
    oszlop = max;
  }
  for (i = 1; i <= sor; i++)
  {
    for (j = 1; j <= oszlop; j++)
    {
      printf("%d ∗ %d = %d \t ", i, j, i * j);
    }
    printf("\n");
  }
  return sor * oszlop;
}

int beker()
{
  int a, limit = 2;
  do
  {
    scanf("%d\n", &a);
  } while (a <= limit);
  return a;
}

int maxatlag(int db)
{
  int i, max, aktualisszam;
  float osszeg = 0;
  printf("1. szam: ");
  scanf("%d", &aktualisszam);
  max = aktualisszam;
  for (i = 2; i <= db; i++)
  {
    printf("%d. szam:", i);
    scanf("%d\n", &aktualisszam);
    if (aktualisszam > max)
    {
      max = aktualisszam;
    }
    osszeg += aktualisszam;
  }
  printf("max: %d, atlag: %f\n", max, osszeg / db);
  return max;
}

int faktor(int szam)
{
  int i, fakt = 1, limit = 10;
  if (szam > limit)
  {
    szam = limit;
  }
  for (i = 1; i <= szam; i++)
  {
    fakt *= i;
  }
  printf("Faktorialis erteke: %d\n", fakt);
  return fakt;
}
