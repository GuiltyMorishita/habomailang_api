levels = [1, 2, 3, 4, 5]

50.times do
  levels.each do |level|
    sentence = Faker::Lorem.sentence(3)
    Noodle.create(level: level, sentence: sentence)
  end
end

50.times do
  levels.each do |level|
    sentence = Faker::Lorem.sentence(3)
    Soup.create(level: level, sentence: sentence)
  end
end

50.times do
  levels.each do |level|
    sentence = Faker::Lorem.sentence(3)
    Pork.create(level: level, sentence: sentence)
  end
end
