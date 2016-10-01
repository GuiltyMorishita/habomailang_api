Rails.application.routes.draw do
  get "api", to: "api#sentence_generator"
end
