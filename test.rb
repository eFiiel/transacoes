#!/usr/bin/ruby -w

require "faraday"
require "json"
require "pp"
require "io/console"



def menu
  system("clear")
  puts("     Bem Vindo a Furst&Fiel\r")
  puts("Digite 1 para listar as passagens")
  puts("Digite 2 para comprar passagens")
  puts("Digite 3 para listar hospedagens")
  puts("Digite 4 para reservar um quarto")
  puts("Digite 5 para comprar pacotes")
  puts("Digite 0 para sair")
  cmd = gets

  if cmd == "1\n"
    list_ticks
    puts "\nPressione qualquer tecla para voltar ao menu\n"
    STDIN.getch
    puts "\n\n"
    system("clear")
    menu
  elsif cmd == "2\n"
    buy_ticks
    puts "\nPressione qualquer tecla para voltar ao menu\n"
    STDIN.getch
    puts "\n\n"
    system("clear")
    menu
  elsif cmd == "3\n"
    list_hotel
    puts "\nPressione qualquer tecla para voltar ao menu\n"
    STDIN.getch
    puts "\n\n"
    system("clear")
    menu
  elsif cmd == "4\n"
    buy_hotel
    puts "\nPressione qualquer tecla para voltar ao menu\n"
    STDIN.getch
    puts "\n\n"
    system("clear")
    menu
  elsif cmd == "5\n"
    buy_packs
    puts "\nPressione qualquer tecla para voltar ao menu\n"
    STDIN.getch
    puts "\n\n"
    system("clear")
    menu
  elsif cmd == "0\n"
    system("clear")
    system("exit")
  else
    puts("Comando Inválido")
    puts "\nPressione qualquer tecla para voltar ao menu\n"
    STDIN.getch
    puts "\n"
    system("clear")
    menu
  end
end

def getTipo
  puts("Digite 1 para ida e volta e 2 para somente ida: ")
  gets
end


def buy_ticks
  puts("Digite sua origem: ")
  origem = gets
  puts ("Digite seu destino: ")
  destino = gets
  tipo = getTipo
  while true
    if tipo == "1\n"
      puts("Digite a data de ida no formato DD/MM/YYYY: ")
      dataida = gets
      puts("Digite a data de volta no formato DD/MM/YYYY: ")
      datavolta = gets
      break
    elsif tipo == "2\n"
      puts("Digite a data da viagem no formato DD/MM/YYYY: ")
      dataida = gets
      break
    else
      puts("Opção inválida !")
      tipo = getTipo
    end
    if tipo != "1\n" and tipo != "2\n"
      continue
    end
  end
  puts("Quantidade de passagens: ")
  npessoas = gets
  response = Faraday.new "http://127.0.0.1:8000" do |faraday|
    faraday.request :url_encoded
    #faraday.response :logger
    faraday.adapter :net_http

  end
  vetor =response.get '/CPpassagens/' do |req|
    req.params['org'] = origem
    req.params['dst'] = destino
    req.params['qtd'] = npessoas
    req.params['ida'] = dataida
    req.params['volta'] = datavolta
  end
  vetor = JSON.parse(vetor.body)
  if vetor == []
    puts "\n\nItens não encontrados"
  else
    puts "\n\nItens comprados:\n"
  end
  for i in vetor
    puts "Origem:  " + i['origem']
    puts "Destino: " + i['destino']
    puts "Vagas:   " + String(i['vagas'])
    puts "Data:    " + i['data'] + "\n\n"

  end

end


def list_ticks
  puts("\n\nPassagens Aéreas:   \n\n")
  response = Faraday.new "http://127.0.0.1:8000/LSpassagens/"
  vetor =JSON.parse(response.get.body)
  for i in vetor
    puts "Origem:  " + i['origem']
    puts "Destino: " + i['destino']
    puts "Vagas:   " + String(i['vagas'])
    puts "Data:    " + i['data'] + "\n\n"

  end

end


def list_hotel
  response = Faraday.new "http://127.0.0.1:8000/LShospedagens/"
  vetor =JSON.parse(response.get.body)
  puts("\n\n   Vagas de Hospedagens:\n\n ")
  for i in vetor
    puts "Cidade:          " + i['local']
    puts "Nº de quartos:   " + String(i['quartos'])
    puts "Data:            " + i['data'] + "\n\n"
  end
end


def buy_hotel
  puts("Cidade: ")
  cidade = gets
  puts("Data de Entrada no formato DD/MM/YYYY: ")
  ent = gets
  puts("Data de Saída no formato DD/MM/YYYY: ")
  sai = gets
  puts("Número de Quartos: ")
  nqts = gets
  response = Faraday.new "http://127.0.0.1:8000" do |faraday|
    faraday.request :url_encoded
    #faraday.response :logger
    faraday.adapter :net_http

  end
  vetor =response.get '/CPhospedagens/' do |req|
    req.params['city'] = cidade
    req.params['in'] = ent
    req.params['out'] = sai
    req.params['qts'] = nqts

  end
  vetor = JSON.parse(vetor.body)
  if vetor == []
    puts "\n\nItens não encontrados"
  else
    puts "\n\nItens comprados:\n"
  end
  for i in vetor
    puts "Cidade:  " + i['local']
    puts "Quartos: " + String(i['quartos'])
    puts "Data:    " + i['data'] + "\n\n"

  end

end


def buy_packs
  puts("Origem: ")
  org = gets
  puts("Destino: ")
  dst = gets
  puts("Data de Ida no formato DD/MM/YYYY: ")
  ent = gets
  puts("Data de Volta no formato DD/MM/YYYY: ")
  sai = gets
  puts("Número de Quartos: ")
  nqts = gets
  puts("Número de Pessoas: ")
  npep = gets
  response = Faraday.new "http://127.0.0.1:8000" do |faraday|
    faraday.request :url_encoded
    #faraday.response :logger
    faraday.adapter :net_http

  end
  vetor =response.get '/CPpacotes/' do |req|
    req.params['org'] = org
    req.params['dst'] = dst
    req.params['ida'] = ent
    req.params['volta'] = sai
    req.params['qts'] = nqts
    req.params['people'] = npep

  end
  vetor = JSON.parse(vetor.body)

  if not vetor == [] and vetor
    puts "\n\nItens comprados:\n"
    for i in vetor
      if i['origem']
        puts "Origem:          " + i['origem']
      end
      if i['destino']
        puts "Destino:         " + i['destino']
      end
      if i['local']
        puts "Cidade:          " + i['local']
      end
      if i['quartos']
        puts "Nº de quartos:   " + String(i['quartos'])
      end
      if i['vagas']
        puts "Nº de pessoas:   " + String(i['vagas'])
      end
      if i['data']
      puts "Data:            " + i['data'] + "\n\n"
      end
    end
  else
    puts "\n\nItens não encontrados"
  end
end


menu

