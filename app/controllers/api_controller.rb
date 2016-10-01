class ApiController < ApplicationController
  def sentence_generator

    shop_name = params[:shop_name]
    menu = params[:menu]
    topping = params[:topping]
    price = params[:price]
    noodle_level = params[:noodle_level]
    soup_level = params[:soup_level]
    pork_level = params[:pork_level]

    noodle_sentence = ""
    soup_sentence = ""
    pork_sentence = ""

    # pythonスクリプトの実行
    system("python #{Rails.root}/TextGenerator/PrepareChain_noodle#{noodle_level}.py")
    system("python #{Rails.root}/TextGenerator/GenerateText.py")

    File.open('output.txt') do |file|
      # labmenには読み込んだ行が含まれる
      noodle_sentence = "麺、" + file.readline
    end

    # pythonスクリプトの実行
    system("python #{Rails.root}/TextGenerator/PrepareChain_soup#{soup_level}.py")
    system("python #{Rails.root}/TextGenerator/GenerateText.py")

    File.open('output.txt') do |file|
      # labmenには読み込んだ行が含まれる
      soup_sentence = "汁、" + file.readline
    end

    # pythonスクリプトの実行
    system("python #{Rails.root}/TextGenerator/PrepareChain_pork#{pork_level}.py")
    system("python #{Rails.root}/TextGenerator/GenerateText.py")

    File.open('output.txt') do |file|
      # labmenには読み込んだ行が含まれる
      pork_sentence = "豚、" + file.readline
    end

    youbi = %w[日 月 火 水 木 金 土]
    date = Date.today.to_era("%O%E年%m月%d日") + youbi[Date.today.wday] + "曜日"
    sentence = date + "、" + shop_name + "、" + menu + " " + topping + " " + price + "YEN\n"
    sentence += noodle_sentence + "\n"
    sentence += soup_sentence + "\n"
    sentence += pork_sentence + "\n"
    sentence += "完飲。"


    request = { sentence: sentence }
    render :json => request
  end


  private
  def api_params
    params.permit(:shop_name, :menu, :topping, :price, :noodle_level, :soup_level, :pork_level)
  end
end
