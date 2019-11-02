#!/opt/local/bin/ruby -w

ARGV.each do |filename|
  sum_abs_diffs = 0.0
  file = File.new(filename, "r")
  while line = file.gets
    tokens = line.split
    sum_abs_diffs = sum_abs_diffs + tokens[2].to_f.abs
  end
  print "%20s %8.4f\n" % [filename, sum_abs_diffs]
end
